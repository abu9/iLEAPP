import json
import os
import re
from datetime import datetime, timezone
import pytz
from PIL import Image
from pillow_heif import register_heif_opener

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import (
    logfunc,
    tsv,
    timeline,
    kmlgen,
    is_platform_windows,
    media_to_html,
    open_sqlite_db_readonly,
    guess_mime
)
from scripts.photo_renderer import photo_HTML, render_photo_script


def isclose(a, b, rel_tol=1e-06, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def get_exif(filename):
    """
    Only retrieve GPS IFD (0x8825). Return None if the file lacks EXIF/GPS.
    """
    try:
        with Image.open(filename) as img:
            getexif = getattr(img, "getexif", None)
            if getexif is None:
                return None

            exif = getexif()
            if not exif:
                return None

            try:
                return exif.get_ifd(0x8825)
            except Exception:
                return None
    except Exception as ex:
        logfunc(f'get_exif() failed on {filename}: {ex}')
        return None


def get_all_exif(filename):
    """
    Return the full EXIF dict; on failure return an empty dict without raising.
    """
    try:
        with Image.open(filename) as img:
            getexif = getattr(img, "getexif", None)
            if getexif is None:
                return {}
            exif = getexif()
            return exif if exif else {}
    except Exception as ex:
        logfunc(f'get_all_exif() failed on {filename}: {ex}')
        return {}


def get_geotagging(exif):
    geo_tagging_info = {}
    if not exif:
        return None

    gps_keys = [
        'GPSVersionID', 'GPSLatitudeRef', 'GPSLatitude', 'GPSLongitudeRef',
        'GPSLongitude', 'GPSAltitudeRef', 'GPSAltitude', 'GPSTimeStamp',
        'GPSSatellites', 'GPSStatus', 'GPSMeasureMode', 'GPSDOP',
        'GPSSpeedRef', 'GPSSpeed', 'GPSTrackRef', 'GPSTrack',
        'GPSImgDirectionRef', 'GPSImgDirection', 'GPSMapDatum',
        'GPSDestLatitudeRef', 'GPSDestLatitude', 'GPSDestLongitudeRef',
        'GPSDestLongitude', 'GPSDestBearingRef', 'GPSDestBearing',
        'GPSDestDistanceRef', 'GPSDestDistance', 'GPSProcessingMethod',
        'GPSAreaInformation', 'GPSDateStamp', 'GPSDifferential'
    ]

    for k, v in exif.items():
        try:
            geo_tagging_info[gps_keys[k]] = str(v)
        except IndexError:
            # Ignore indexes that are not listed in gps_keys
            pass
    return geo_tagging_info


def _get_asset_table_and_columns(db, db_path):
    """
    Detect at runtime the primary asset table in Photos.sqlite (ZASSET or ZGENERICASSET)
    and return:
      - asset_table: actual table name in use
      - asset_cols: column names of that table
      - add_cols: column names of ZADDITIONALASSETATTRIBUTES (if present)
      - has_additional: whether ZADDITIONALASSETATTRIBUTES exists
    """
    cursor = db.cursor()

    # Check asset tables
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name IN ('ZASSET','ZGENERICASSET')
    """)
    table_rows = cursor.fetchall()
    if not table_rows:
        logfunc(f'Photos.sqlite: neither ZASSET nor ZGENERICASSET found in {db_path}')
        return None, set(), set(), False

    # If both exist, sort names (ZASSET first)
    asset_table = sorted({row[0] for row in table_rows})[0]

    def get_columns(table_name):
        cursor.execute(f"PRAGMA table_info({table_name})")
        return {row[1] for row in cursor.fetchall()}

    asset_cols = get_columns(asset_table)

    # Additional attributes table
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name='ZADDITIONALASSETATTRIBUTES'
    """)
    has_additional = bool(cursor.fetchall())
    add_cols = get_columns('ZADDITIONALASSETATTRIBUTES') if has_additional else set()

    return asset_table, asset_cols, add_cols, has_additional


def _build_photos_query(asset_table, asset_cols, add_cols, has_additional):
    """
    Build SQL using only columns that actually exist.
    Returns (sql, uses_lat_lon):
      - sql: final SELECT statement
      - uses_lat_lon: whether latitude/longitude columns are truly read from the DB
    """
    select_cols = []

    # ZDATECREATED
    if 'ZDATECREATED' in asset_cols:
        select_cols.append(
            f"DATETIME({asset_table}.ZDATECREATED+978307200,'UNIXEPOCH') AS DATECREATED"
        )
    else:
        select_cols.append("NULL AS DATECREATED")

    # ZMODIFICATIONDATE
    if 'ZMODIFICATIONDATE' in asset_cols:
        select_cols.append(
            f"DATETIME({asset_table}.ZMODIFICATIONDATE+978307200,'UNIXEPOCH') AS MODIFICATIONDATE"
        )
    else:
        select_cols.append("NULL AS MODIFICATIONDATE")

    # Path fields
    if 'ZDIRECTORY' in asset_cols:
        select_cols.append(f"{asset_table}.ZDIRECTORY AS DIRECTORY")
    else:
        select_cols.append("NULL AS DIRECTORY")

    if 'ZFILENAME' in asset_cols:
        select_cols.append(f"{asset_table}.ZFILENAME AS FILENAME")
    else:
        select_cols.append("NULL AS FILENAME")

    uses_lat_lon = False

    # Coordinates: prefer asset table, then additional attributes table, else NULL
    if 'ZLATITUDE' in asset_cols and 'ZLONGITUDE' in asset_cols:
        select_cols.append(f"{asset_table}.ZLATITUDE AS LATITUDE")
        select_cols.append(f"{asset_table}.ZLONGITUDE AS LONGITUDE")
        uses_lat_lon = True
    elif 'ZLATITUDE' in add_cols and 'ZLONGITUDE' in add_cols:
        select_cols.append("ZADDITIONALASSETATTRIBUTES.ZLATITUDE AS LATITUDE")
        select_cols.append("ZADDITIONALASSETATTRIBUTES.ZLONGITUDE AS LONGITUDE")
        uses_lat_lon = True
    else:
        select_cols.append("NULL AS LATITUDE")
        select_cols.append("NULL AS LONGITUDE")

    # Bundle ID
    if has_additional and 'ZCREATORBUNDLEID' in add_cols:
        select_cols.append("ZADDITIONALASSETATTRIBUTES.ZCREATORBUNDLEID AS CREATORBUNDLEID")
    else:
        select_cols.append("NULL AS CREATORBUNDLEID")

    join_sql = ""
    if has_additional:
        join_sql = (
            f" INNER JOIN ZADDITIONALASSETATTRIBUTES "
            f"ON {asset_table}.Z_PK = ZADDITIONALASSETATTRIBUTES.Z_PK"
        )

    select_sql = ",\n            ".join(select_cols)

    query = f"""
        SELECT
            {select_sql}
        FROM {asset_table}
        {join_sql}
    """

    return query, uses_lat_lon


def _match_photo_files(files_found, zdirectory, zfilename):
    """
    Try to find the decrypted file path matching (zdirectory, zfilename) in files_found.
    Return the first matched path string, or None if not found.
    """
    if not zdirectory or not zfilename:
        return None

    path_parts = str(zdirectory).split('/')
    if len(path_parts) < 2:
        return None

    part0, part1 = path_parts[0], path_parts[1]

    for search in files_found:
        search = str(search)
        if part0 in search and part1 in search and str(zfilename) in search:
            return search

    return None


def _build_thumbnail(search_path, zfilename, report_folder, files_found):
    """
    Build thumbnail HTML based on file type.
    """
    thumb = ''

    searchbase = os.path.basename(search_path)

    if search_path.upper().endswith('HEIC'):
        try:
            register_heif_opener()
            with Image.open(search_path) as image:
                convertedfilepath = os.path.join(report_folder, f'{searchbase}.jpg')
                image.save(convertedfilepath)
            convertedlist = [convertedfilepath]
            thumb = media_to_html(f'{searchbase}.jpg', convertedlist, report_folder)
        except Exception as ex:
            logfunc(f'Error converting HEIC to JPG for {search_path}: {ex}')
    elif (search_path.upper().endswith('JPG') or
          search_path.upper().endswith('PNG') or
          search_path.upper().endswith('JPEG')):
        thumb = media_to_html(zfilename, files_found, report_folder)

    return thumb


def _extract_media_paths(media_html: str):
    if not media_html:
        return "", ""
    href_match = re.search(r'href="([^"]+)"', media_html)
    img_match = re.search(r'src="([^"]+)"', media_html)
    img_src = img_match.group(1) if img_match else ""
    href_src = href_match.group(1) if href_match else ""
    return img_src, href_src or img_src


def _stringify_field(value):
    if value is None:
        return ""
    return str(value)


def _encode_json_for_script_tag(data):
    # Escape a closing </script> so injected data cannot break out of the JSON block
    return json.dumps(data, ensure_ascii=False).replace('</', '<\\/')


def _parse_datetime(value: str):
    if not value:
        return None
    value = value.strip()
    if not value:
        return None
    formats = (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y:%m:%d %H:%M:%S",
        "%Y:%m:%d %H:%M:%S.%f",
    )
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except (ValueError, TypeError):
            continue
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def _apply_file_mtime(target_path: str, timestamp: datetime):
    if not target_path or timestamp is None:
        return
    try:
        if timestamp.tzinfo is not None:
            timestamp = timestamp.astimezone(timezone.utc)
        else:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        ts = timestamp.timestamp()
        os.utime(target_path, (ts, ts))
    except Exception as ex:
        logfunc(f"Failed updating mtime for {target_path}: {ex}")


def _update_file_mtime(matched_path: str, creationchanged: str, zdatecreated: str):
    if not matched_path:
        return
    dt_exif = _parse_datetime(creationchanged)
    dt_db = _parse_datetime(zdatecreated)
    selected = dt_exif or dt_db
    _apply_file_mtime(matched_path, selected)


def _extract_exif_and_compare(search_path, zdatecreated, zlatitude, zlongitude):
    """
    Read EXIF/GPS and compare with DB coordinates and timestamps.
    Returns:
      suspecttime, offset, suspectcoordinates, creationchanged, latitude, longitude, exifdata
    """
    suspecttime = ''
    offset = ''
    suspectcoordinates = ''
    creationchanged = ''
    latitude = ''
    longitude = ''
    exifdata = ''

    # Only attempt EXIF for common image formats
    if not (search_path.upper().endswith('JPG') or
            search_path.upper().endswith('PNG') or
            search_path.upper().endswith('JPEG') or
            search_path.upper().endswith('HEIC')):
        return suspecttime, offset, suspectcoordinates, creationchanged, latitude, longitude, exifdata

    try:
        image_info = get_exif(search_path)
        results = get_geotagging(image_info)

        # Coordinates
        if results is None:
            latitude = ''
            longitude = ''
        else:
            directionlat = results.get('GPSLatitudeRef')
            latitude_raw = results.get('GPSLatitude')
            directionlon = results.get('GPSLongitudeRef')
            longitude_raw = results.get('GPSLongitude')

            if latitude_raw and directionlat:
                lat_parts = (
                    latitude_raw.replace('(', '')
                    .replace(')', '')
                    .split(', ')
                )
                latitude = (
                    float(lat_parts[0]) +
                    float(lat_parts[1]) / 60 +
                    float(lat_parts[2]) / (60 * 60)
                )
                if directionlat in ['W', 'S']:
                    latitude *= -1
            else:
                latitude = ''

            if longitude_raw and directionlon:
                lon_parts = (
                    longitude_raw.replace('(', '')
                    .replace(')', '')
                    .split(', ')
                )
                longitude = (
                    float(lon_parts[0]) +
                    float(lon_parts[1]) / 60 +
                    float(lon_parts[2]) / (60 * 60)
                )
                if directionlon in ['W', 'S']:
                    longitude *= -1
            else:
                longitude = ''

        # All EXIF text
        exifall = get_all_exif(search_path)
        for x, y in exifall.items():
            if x == 271:
                exifdata += f'Manufacturer: {y}<br>'
            elif x == 272:
                exifdata += f'Model: {y}<br>'
            elif x == 305:
                exifdata += f'Software: {y}<br>'
            elif x == 274:
                exifdata += f'Orientation: {y}<br>'
            elif x == 306:
                exifdata += f'Creation/Changed: {y}<br>'
                creationchanged = y
            elif x == 282:
                exifdata += f'Resolution X: {y}<br>'
            elif x == 283:
                exifdata += f'Resolution Y: {y}<br>'
            elif x == 316:
                exifdata += f'Host device: {y}<br>'
            else:
                exifdata += f'{x}: {y}<br>'

        # Coordinate comparison (only when DB and EXIF both have float values)
        if isinstance(zlatitude, float) and isinstance(latitude, float):
            suspectA = isclose(zlatitude, latitude)
            if isinstance(zlongitude, float) and isinstance(longitude, float):
                suspectB = isclose(zlongitude, longitude)
                if suspectA and suspectB:
                    suspectcoordinates = 'True'
                else:
                    suspectcoordinates = 'False'
            else:
                suspectcoordinates = ''
        else:
            suspectcoordinates = ''

        # Time comparison: DB time is UTC, EXIF is usually local time
        if creationchanged and zdatecreated:
            mytz = pytz.timezone('UTC')

            try:
                dbdate = datetime.fromisoformat(zdatecreated)
                dbdate = mytz.normalize(mytz.localize(dbdate, is_dst=True))
            except Exception:
                dbdate = None

            exifdate = creationchanged.replace(':', '-', 2)
            creationchanged = exifdate
            exifdate_trim = exifdate[:-1]

            responsive = ''
            suspecttime = 'False'
            offset = ''

            if dbdate:
                time_list = []
                for timeZone in pytz.all_timezones:
                    dbtimezonedate = dbdate.astimezone(pytz.timezone(timeZone))
                    time_list.append((str(dbtimezonedate), timeZone))

                for dt_str, _tz_name in time_list:
                    if exifdate_trim in dt_str:
                        responsive = dt_str
                        suspecttime = 'True'
                        break
                    elif exifdate_trim[:-1] in dt_str[:-7]:
                        responsive = dt_str
                        suspecttime = 'True'
                        break
                    elif exifdate_trim[:-2] in dt_str[:-8]:
                        responsive = dt_str
                        suspecttime = 'True'
                        break

                if responsive:
                    offset = responsive[-6:]

    except Exception as ex:
        logfunc(f'Error getting exif on: {search_path} ({ex})')

    return suspecttime, offset, suspectcoordinates, creationchanged, latitude, longitude, exifdata


def get_photosDbexif(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)

        filename = os.path.basename(file_found)
        if not filename.lower().endswith('photos.sqlite'):
            # Only process Photos.sqlite
            continue

        data_list = []

        db = open_sqlite_db_readonly(file_found)
        try:
            asset_table, asset_cols, add_cols, has_additional = _get_asset_table_and_columns(db, file_found)
            if not asset_table:
                db.close()
                continue

            query, _ = _build_photos_query(asset_table, asset_cols, add_cols, has_additional)

            cursor = db.cursor()
            cursor.execute(query)
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)

        except Exception as ex:
            logfunc(f'Error executing Photos.sqlite query ({filename}) at {file_found}: {ex}')
            all_rows = []
            usageentries = 0
        finally:
            db.close()

        if usageentries <= 0:
            logfunc('No Photos.sqlite Analysis data available')
            continue

        matched_paths = []
        # Process each DB record
        for row in all_rows:
            (thumb, suspecttime, suspectcoordinates,
             zdatecreated, zmodificationdate, zdirectory, zfilename,
             zlatitude, zlongitude, creationchanged,
             latitude, longitude, exifdata, zbundlecreator) = (
                '', '', '', '', '', '', '',
                '', '', '', '', '', '', ''
            )

            zdatecreated = row[0]
            zmodificationdate = row[1]
            zdirectory = row[2]
            zfilename = row[3]
            zlatitude = row[4]
            zlongitude = row[5]
            zbundlecreator = row[6]

            # Find matching file
            matched_path = _match_photo_files(files_found, zdirectory, zfilename)
            if not matched_path:
                continue

            # Thumbnail
            thumb = _build_thumbnail(matched_path, zfilename, report_folder, files_found)

            # EXIF and comparisons
            (suspecttime, offset, suspectcoordinates,
             creationchanged, latitude, longitude, exifdata) = _extract_exif_and_compare(
                matched_path, zdatecreated, zlatitude, zlongitude
            )

            _update_file_mtime(matched_path, creationchanged, zdatecreated)
            matched_paths.append(matched_path)
            data_list.append(
                (
                    thumb,
                    suspecttime,
                    offset,
                    suspectcoordinates,
                    zdatecreated,
                    zmodificationdate,
                    zdirectory,
                    zfilename,
                    zlatitude,
                    zlongitude,
                    creationchanged,
                    latitude,
                    longitude,
                    exifdata,
                    zbundlecreator
                )
            )

        if data_list:
            description = (
                'All times labeled as False require validation. Compare database times and '
                'geolocation points to their EXIF counterparts. Timestamp value is in UTC. '
                'Exif Creation/Change timestamp is on local time. Use Possible Exif Offset '
                'column value to compare the times.'
            )
            report = ArtifactHtmlReport('Photos.sqlite Analysis')
            report.start_artifact_report(report_folder, 'Photos.sqlite Analysis', description)

            rows_json = []
            for index, entry in enumerate(data_list):
                thumb_html, *fields = entry
                thumb_src, preview_src = _extract_media_paths(thumb_html)
                rows_json.append({
                    "thumb": thumb_src,
                    "preview": preview_src or thumb_src,
                    "mediaType": guess_mime(matched_paths[index]) or "",
                    "fields": [_stringify_field(value) for value in fields]
                })

            data_json = _encode_json_for_script_tag(rows_json)
            report.write_lead_text(f'Total number of entries: {len(data_list)}')
            report.write_lead_text(f'Photos.sqlite Analysis located at: {file_found}')
            report.write_raw_html(photo_HTML.replace("__DATA_JSON__", data_json))
            report.add_script(render_photo_script())
            report.end_artifact_report()

            data_headers = (
                'Media',
                'Same Timestamps?',
                'Possible Exif Offset',
                'Same Coordinates?',
                'Timestamp',
                'Timestamp Modification',
                'Directory',
                'Filename',
                'Latitude DB',
                'Longitude DB',
                'Exif Creation/Changed',
                'Latitude',
                'Longitude',
                'Exif',
                'Bundle Creator'
            )

            # TSV / Timeline do not support tuple headers; flatten safely
            timeline_headers = tuple(
                h[0] if isinstance(h, tuple) else h
                for h in data_headers
            )

            tsvname = 'Photos.sqlite Analysis'
            tsv(report_folder, timeline_headers, data_list, tsvname)

            tlactivity = 'Photos.sqlite Analysis'
            timeline(report_folder, tlactivity, data_list, timeline_headers)
        else:
            logfunc('No Photos.sqlite Analysis data available')


__artifacts__ = {
    "photosDbexif": (
        "Photos",
        ('*Media/PhotoData/Photos.sqlite*', '*Media/DCIM/*/**'),
        get_photosDbexif
    )
}

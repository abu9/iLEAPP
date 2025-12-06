import os
from datetime import datetime
from pathlib import Path

import pytz
from PIL import Image
from pillow_heif import register_heif_opener

from scripts.artifact_report import ArtifactHtmlReport  # 兼容旧 wrapper，虽然不直接用
from scripts.ilapfuncs import (
    logfunc,
    open_sqlite_db_readonly,
    check_in_media,
)


def isclose(a, b, rel_tol=1e-06, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def get_exif(filename):
    image = Image.open(filename)
    image.verify()
    return image.getexif().get_ifd(0x8825)


def get_all_exif(filename):
    image = Image.open(filename)
    image.verify()
    return image.getexif()


def get_geotagging(exif):
    """把 EXIF GPS IFD 转成更好用的 dict，可能返回 None。"""
    if not exif:
        return None

    gps_keys = [
        "GPSVersionID", "GPSLatitudeRef", "GPSLatitude", "GPSLongitudeRef", "GPSLongitude",
        "GPSAltitudeRef", "GPSAltitude", "GPSTimeStamp", "GPSSatellites", "GPSStatus",
        "GPSMeasureMode", "GPSDOP", "GPSSpeedRef", "GPSSpeed", "GPSTrackRef", "GPSTrack",
        "GPSImgDirectionRef", "GPSImgDirection", "GPSMapDatum", "GPSDestLatitudeRef",
        "GPSDestLatitude", "GPSDestLongitudeRef", "GPSDestLongitude", "GPSDestBearingRef",
        "GPSDestBearing", "GPSDestDistanceRef", "GPSDestDistance", "GPSProcessingMethod",
        "GPSAreaInformation", "GPSDateStamp", "GPSDifferential",
    ]

    geo_tagging_info = {}
    for k, v in exif.items():
        try:
            geo_tagging_info[gps_keys[k]] = str(v)
        except IndexError:
            # 未知的 GPS tag index，直接跳过
            continue
    return geo_tagging_info


def _table_exists(cursor, table_name):
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    )
    return cursor.fetchone() is not None


def _detect_asset_table(cursor):
    """
    尝试检测当前 Photos.sqlite 使用哪个主表：
    - 新: ZASSET
    - 旧: ZGENERICASSET
    返回表名字符串，或 None。
    """
    if _table_exists(cursor, "ZASSET"):
        return "ZASSET"
    if _table_exists(cursor, "ZGENERICASSET"):
        return "ZGENERICASSET"
    return None


def _build_media_index(files_found):
    """
    建一个 { (directory, filename): full_extracted_path } 索引，
    方便按 ZDIRECTORY / ZFILENAME 反查解密后的真实文件路径。

    directory 格式尽量对齐 DB：
      - 如果真实路径里有 .../Media/DCIM/100APPLE/IMG_xxx.JPG
        那么 key 就是 ('DCIM/100APPLE', 'IMG_xxx.JPG')
    """
    index = {}

    for path in files_found:
        lower = path.lower()
        if not lower.endswith((".jpg", ".jpeg", ".png", ".heic")):
            continue

        norm = path.replace("\\", "/")
        lower_norm = norm.lower()
        media_pos = lower_norm.find("/media/")
        if media_pos == -1:
            # 不在 Media 下的图片（比如别的应用私有路径），此处先不管
            continue

        after_media = norm[media_pos + len("/media/"):]  # 比如 'DCIM/100APPLE/IMG_0001.JPG'
        if "/" not in after_media:
            # 没有子目录，不是典型 DCIM 结构
            continue

        dir_part, filename = after_media.rsplit("/", 1)
        key = (dir_part, filename)
        index[key] = path

    return index


def _match_media_path(media_index, zdirectory, zfilename):
    """
    根据 DB 里的 ZDIRECTORY / ZFILENAME，在 media_index 里面找文件路径。
    兼容几种常见目录写法：
      - 'DCIM/100APPLE'
      - '100APPLE'
    """
    if not zdirectory:
        return None

    zdirectory = zdirectory.strip("/")

    candidates = [zdirectory]
    if not zdirectory.lower().startswith("dcim/"):
        candidates.append(f"DCIM/{zdirectory}")

    for d in candidates:
        key = (d, zfilename)
        if key in media_index:
            return media_index[key]

    return None


def get_photosDbexif(context):
    """
    Photos.sqlite + EXIF 比对：
    - 从 Photos.sqlite(ZASSET / ZGENERICASSET) 读出
      时间、目录、文件名、DB 中经纬度、Bundle ID
    - 在已解密出的 DCIM 目录中查找对应文件
    - 解析 EXIF 时间和经纬度
    - 比较 DB 与 EXIF 的时间 / 坐标是否一致
    - 使用 check_in_media 注册媒体文件（给 LAVA / 报表使用）
    """

    files_found = context.files_found
    report_folder = context.report_folder  # 未直接用，但保留以防后续扩展
    seeker = context.seeker                # 未直接用
    timezone_offset = context.timezone_offset  # 未直接用，但保留接口一致性

    # 找 Photos.sqlite
    photos_dbs = [f for f in files_found if f.endswith("Photos.sqlite")]
    if not photos_dbs:
        logfunc("PhotosDbexif: No Photos.sqlite found")
        return [], [], ""

    source_file = photos_dbs[0]  # 通常只有一个，先按一个处理

    # 先把所有图片路径索引起来： (ZDIRECTORY, ZFILENAME) -> extracted_path
    media_index = _build_media_index(files_found)

    data_list = []

    db = open_sqlite_db_readonly(source_file)
    cursor = db.cursor()

    asset_table = _detect_asset_table(cursor)
    if not asset_table:
        logfunc(
            "PhotosDbexif: Neither ZASSET nor ZGENERICASSET found in Photos.sqlite; "
            "unsupported schema."
        )
        db.close()
        return [], [], source_file

    # 构造针对不同主表的 SQL
    query = f"""
        SELECT
            DATETIME({asset_table}.ZDATECREATED+978307200,'UNIXEPOCH') AS DATECREATED,
            DATETIME({asset_table}.ZMODIFICATIONDATE+978307200,'UNIXEPOCH') AS MODIFICATIONDATE,
            {asset_table}.ZDIRECTORY,
            {asset_table}.ZFILENAME,
            {asset_table}.ZLATITUDE,
            {asset_table}.ZLONGITUDE,
            ZADDITIONALASSETATTRIBUTES.ZCREATORBUNDLEID
        FROM {asset_table}
        LEFT JOIN ZADDITIONALASSETATTRIBUTES
            ON {asset_table}.Z_PK = ZADDITIONALASSETATTRIBUTES.Z_PK
    """

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
    except Exception as ex:
        logfunc(f"PhotosDbexif: Error querying {asset_table} from Photos.sqlite - {ex}")
        db.close()
        return [], [], source_file

    db.close()

    if not rows:
        logfunc("PhotosDbexif: No asset rows found in Photos.sqlite")
        return [], [], source_file

    # 为可能的 HEIC 添加支持
    try:
        register_heif_opener()
    except Exception:
        # pillow-heif 不可用也无所谓，只是 HEIC 可能无法读 EXIF
        pass

    for row in rows:
        (
            zdatecreated,
            zmodificationdate,
            zdirectory,
            zfilename,
            zlatitude,
            zlongitude,
            zbundlecreator,
        ) = row

        media_path = _match_media_path(media_index, zdirectory or "", zfilename or "")
        media_ref = None
        suspect_time = ""
        suspect_coordinates = ""
        offset = ""
        creationchanged = ""
        latitude = ""
        longitude = ""
        exifdata = ""

        # 默认: 坐标是否一致 = 空（未知）
        suspect_coordinates = ""

        # 如果能在解密后的文件中找到实际文件，再去跑 EXIF 与 GPS
        if media_path and os.path.exists(media_path):
            try:
                # 注册媒体文件（给 LAVA / 报表）
                # 这里直接传已经解密好的绝对路径，避免再次去匹配原始路径。
                media_ref = check_in_media(media_path, name=zfilename)

                lower = media_path.lower()
                if lower.endswith(".heic"):
                    # register_heif_opener 已经调用，这里只是确保可以被 PIL 打开
                    pass

                # EXIF + GPS
                try:
                    gps_ifd = get_exif(media_path)
                    gps_info = get_geotagging(gps_ifd)

                    if gps_info is None:
                        latitude = ""
                        longitude = ""
                    else:
                        # 解析纬度
                        directionlat = gps_info.get("GPSLatitudeRef")
                        lat_raw = gps_info.get("GPSLatitude")
                        if lat_raw:
                            lat_values = (
                                lat_raw.replace("(", "").replace(")", "").split(", ")
                            )
                            lat_deg = float(lat_values[0])
                            lat_min = float(lat_values[1])
                            lat_sec = float(lat_values[2])
                            latitude = (
                                lat_deg
                                + lat_min / 60.0
                                + lat_sec / (60.0 * 60.0)
                            )
                            if directionlat in ["W", "S"]:
                                latitude = -latitude

                        # 解析经度
                        directionlon = gps_info.get("GPSLongitudeRef")
                        lon_raw = gps_info.get("GPSLongitude")
                        if lon_raw:
                            lon_values = (
                                lon_raw.replace("(", "").replace(")", "").split(", ")
                            )
                            lon_deg = float(lon_values[0])
                            lon_min = float(lon_values[1])
                            lon_sec = float(lon_values[2])
                            longitude = (
                                lon_deg
                                + lon_min / 60.0
                                + lon_sec / (60.0 * 60.0)
                            )
                            if directionlon in ["W", "S"]:
                                longitude = -longitude
                except Exception:
                    gps_info = None
                    latitude = ""
                    longitude = ""

                # 把完整 EXIF 列出来，同时提取 Creation/Changed 时间字段
                try:
                    exif_all = get_all_exif(media_path)
                    exifdata_parts = []
                    for tag, value in exif_all.items():
                        if tag == 271:
                            exifdata_parts.append(f"Manufacturer: {value}")
                        elif tag == 272:
                            exifdata_parts.append(f"Model: {value}")
                        elif tag == 305:
                            exifdata_parts.append(f"Software: {value}")
                        elif tag == 274:
                            exifdata_parts.append(f"Orientation: {value}")
                        elif tag == 306:
                            exifdata_parts.append(f"Creation/Changed: {value}")
                            creationchanged = str(value)
                        elif tag == 282:
                            exifdata_parts.append(f"Resolution X: {value}")
                        elif tag == 283:
                            exifdata_parts.append(f"Resolution Y: {value}")
                        elif tag == 316:
                            exifdata_parts.append(f"Host device: {value}")
                        else:
                            exifdata_parts.append(f"{tag}: {value}")
                    exifdata = "<br>".join(exifdata_parts)
                except Exception:
                    exifdata = ""
                    creationchanged = ""

                # DB 坐标 vs EXIF 坐标是否可疑
                if isinstance(zlatitude, float) and isinstance(latitude, float):
                    lat_ok = isclose(zlatitude, latitude)
                else:
                    lat_ok = None

                if isinstance(zlongitude, float) and isinstance(longitude, float):
                    lon_ok = isclose(zlongitude, longitude)
                else:
                    lon_ok = None

                if lat_ok is None or lon_ok is None:
                    suspect_coordinates = ""
                else:
                    suspect_coordinates = "True" if (lat_ok and lon_ok) else "False"

                # DB 时间 vs EXIF 时间差异（通过枚举时区猜 offset）
                if creationchanged and zdatecreated:
                    try:
                        mytz = pytz.timezone("UTC")
                        dbdate = datetime.fromisoformat(zdatecreated)
                        dbdate = mytz.localize(dbdate, is_dst=True)

                        exifdate_str = creationchanged.replace(":", "-", 2)
                        # 有些 EXIF 时间可能没有时区或秒后的小数，这里逐步放宽比对
                        exifdate_trim1 = exifdate_str[:-1]
                        exifdate_trim2 = exifdate_str[:-2]

                        suspect_time = "False"
                        responsive = ""

                        for tzname in pytz.all_timezones:
                            tz = pytz.timezone(tzname)
                            db_tz_time = dbdate.astimezone(tz)
                            db_tz_str = str(db_tz_time)

                            if exifdate_str in db_tz_str:
                                responsive = db_tz_str
                                suspect_time = "True"
                                break
                            if exifdate_trim1 and exifdate_trim1 in db_tz_str[:-7]:
                                responsive = db_tz_str
                                suspect_time = "True"
                                break
                            if exifdate_trim2 and exifdate_trim2 in db_tz_str[:-8]:
                                responsive = db_tz_str
                                suspect_time = "True"
                                break

                        if responsive:
                            offset = responsive[-6:]
                        else:
                            offset = ""
                    except Exception:
                        suspect_time = ""
                        offset = ""

            except Exception as ex:
                logfunc(f"PhotosDbexif: Error processing media file '{media_path}' - {ex}")
                media_ref = None

        # 记录一行。注意第一列是 media 类型，配合 data_headers 里的 ('Media', 'media')
        data_list.append(
            (
                media_ref,           # Media (LAVA media reference)
                suspect_time,        # Same Timestamps?
                offset,              # Possible Exif Offset
                suspect_coordinates, # Same Coordinates?
                zdatecreated,        # Timestamp (DB)
                zmodificationdate,   # Timestamp Modification (DB)
                zdirectory,          # Directory
                zfilename,           # Filename
                zlatitude,           # Latitude DB
                zlongitude,          # Longitude DB
                creationchanged,     # Exif Creation/Changed
                latitude,            # Latitude (EXIF)
                longitude,           # Longitude (EXIF)
                exifdata,            # Exif (HTML)
                zbundlecreator,      # Bundle Creator
            )
        )

    if not data_list:
        logfunc("PhotosDbexif: No Photos.sqlite Analysis data available")
        return [], [], source_file

    logfunc(f"PhotosDbexif: Generated {len(data_list)} rows for Photos.sqlite Analysis")

    # 第一列是 media 类型，告知 LAVA / 报表系统用媒体渲染
    data_headers = (
        ("Media", "media"),
        "Same Timestamps?",
        "Possible Exif Offset",
        "Same Coordinates?",
        "Timestamp",
        "Timestamp Modification",
        "Directory",
        "Filename",
        "Latitude DB",
        "Longitude DB",
        "Exif Creation/Changed",
        "Latitude",
        "Longitude",
        ("Exif", "html"),  # 明确这是 HTML，避免被转义
        "Bundle Creator",
    )

    # context-wrapper 负责 HTML / TSV / Timeline 输出，这里只返回数据
    return data_headers, data_list, source_file


__artifacts__ = {
    "photosDbexif": (
        "Photos",
        ("*Media/PhotoData/Photos.sqlite*", "*Media/DCIM/*/**"),
        get_photosDbexif,
    )
}

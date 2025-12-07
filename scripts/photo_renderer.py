# coding: utf-8
photo_HTML = """
<style>
    :root {
        --photo-table-bg: var(--bs-body-bg, #f8f9fa);
        --photo-table-text: var(--bs-body-color, #212529);
        --photo-border-color: rgba(0, 0, 0, 0.15);
        --photo-stripe-color: rgba(0, 0, 0, 0.04);
    }
    body[data-theme="dark"] {
        --photo-table-bg: #1e1e1e;
        --photo-table-text: #f8f9fa;
        --photo-border-color: rgba(255, 255, 255, 0.15);
        --photo-stripe-color: rgba(255, 255, 255, 0.03);
    }
    .table-shell {
        padding: 1rem;
        border-radius: 16px;
        background: transparent;
        color: var(--photo-table-text);
    }
    .table-wrapper {
        max-height: 70vh;
        overflow: auto;
        border-radius: 12px;
        border: 1px solid var(--photo-border-color);
    }
    table {
        width: 100%;
        min-width: 1300px;
        border-collapse: collapse;
        table-layout: auto;
        background-color: var(--photo-table-bg);
        color: var(--photo-table-text);
    }
    th, td {
        padding: 0.6rem 0.8rem;
        border-bottom: 1px solid var(--photo-border-color);
        border-color: var(--photo-border-color);
        vertical-align: top;
    }
    th:nth-child(1),
    td:nth-child(1) { min-width: 220px; width: 230px; }
    th:nth-child(2),
    td:nth-child(2) { min-width: 130px; }
    th:nth-child(3),
    td:nth-child(3) { min-width: 160px; }
    th:nth-child(4),
    td:nth-child(4) {
        min-width: 135px;
        max-width: 150px;
        white-space: pre-line;
        line-height: 1.25;
    }
    th:nth-child(5),
    td:nth-child(5) {
        min-width: 135px;
        max-width: 150px;
        white-space: pre-line;
        line-height: 1.25;
    }
    th:nth-child(6),
    td:nth-child(6) {
        min-width: 140px;
        max-width: 170px;
        white-space: pre-line;
        line-height: 1.25;
    }
    th:nth-child(7),
    td:nth-child(7) { min-width: 110px; text-align: center; }
    th:nth-child(8),
    td:nth-child(8) { min-width: 110px; text-align: center; }
    th:nth-child(9),
    td:nth-child(9) { min-width: 110px; text-align: center; }
    th:nth-child(10),
    td:nth-child(10) {
        min-width: 110px;
        max-width: 130px;
        text-align: right;
        white-space: normal;
        word-break: break-all;
        line-height: 1.25;
        font-variant-numeric: tabular-nums;
    }
    th:nth-child(11),
    td:nth-child(11) {
        min-width: 110px;
        max-width: 130px;
        text-align: right;
        white-space: normal;
        word-break: break-all;
        line-height: 1.25;
        font-variant-numeric: tabular-nums;
    }
    th:nth-child(12),
    td:nth-child(12) {
        min-width: 110px;
        max-width: 130px;
        text-align: right;
        white-space: normal;
        word-break: break-all;
        line-height: 1.25;
        font-variant-numeric: tabular-nums;
    }
    th:nth-child(13),
    td:nth-child(13) {
        min-width: 110px;
        max-width: 130px;
        text-align: right;
        white-space: normal;
        word-break: break-all;
        line-height: 1.25;
        font-variant-numeric: tabular-nums;
    }
    th:nth-child(14),
    td:nth-child(14) {
        min-width: 220px;
        max-width: 260px;
        word-break: break-word;
        white-space: pre-wrap;
        font-size: 0.9rem;
        line-height: 1.25;
        overflow-y: auto;
    }
    th:nth-child(15),
    td:nth-child(15) { min-width: 120px; }
    th.sortable {
        cursor: pointer;
        user-select: none;
    }
    th.sortable::after {
        content: '^';
        display: inline-block;
        margin-left: 0.35rem;
        font-size: 0.75rem;
        opacity: 0.6;
        transform: translateY(-1px);
        transition: opacity 0.15s ease, transform 0.15s ease, color 0.15s ease;
        color: #7a7a7a;
    }
    th.sorted-asc::after {
        content: '^';
        opacity: 1;
        transform: translateY(-1px);
        color: #444;
    }
    th.sorted-desc::after {
        content: 'v';
        opacity: 1;
        transform: translateY(1px);
        color: #444;
    }
    th {
        position: sticky;
        top: 0;
        z-index: 3;
        font-weight: 600;
        background-color: var(--photo-table-bg);
    }
    th:first-child,
    td:first-child {
        position: sticky;
        left: 0;
        z-index: 4;
        box-shadow: 6px 0 12px rgba(0, 0, 0, 0.05);
    }
    .media-thumb {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 120px;
    }
    .media-thumb img,
    .media-thumb video {
        border-radius: 0.25rem;
        max-width: 180px;
        max-height: 120px;
        width: auto;
        height: auto;
        object-fit: contain;
        background: #000;
    }
    .overlay {
        position: fixed;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(0, 0, 0, 0.85);
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.25s ease, visibility 0.25s ease;
        z-index: 10000;
        backdrop-filter: blur(2px);
    }
    .overlay.show {
        opacity: 1;
        visibility: visible;
    }
    .overlay img,
    .overlay video {
        max-width: 90vw;
        max-height: 90vh;
        border-radius: 0.35rem;
        object-fit: contain;
    }
    .overlay .overlay-image {
        cursor: zoom-in;
    }
    .overlay.zoomed {
        overflow: auto;
        align-items: flex-start;
        justify-content: center;
        padding: 3rem 2rem 2rem;
    }
    .overlay.zoomed .overlay-image {
        max-width: none;
        max-height: none;
        width: auto;
        height: auto;
        object-fit: contain;
        cursor: zoom-out;
        margin: 0 auto;
    }
    .overlay video {
        display: none;
    }
    .overlay .close-btn {
        position: absolute;
        top: 1rem;
        right: 1rem;
        width: 42px;
        height: 42px;
        border-radius: 50%;
        border: none;
        background: rgba(0, 0, 0, 0.7);
        color: #fff;
        font-size: 1.4rem;
        cursor: pointer;
    }
    .overlay-nav {
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        pointer-events: none;
    }
    .nav-btn {
        pointer-events: auto;
        width: 32px;
        height: 32px;
        border-radius: 6px;
        border: 1px solid var(--photo-border-color);
        background: rgba(0, 0, 0, 0.45);
        color: var(--nav-btn-color, #fff);
        font-size: 1.25rem;
        font-weight: bold;
    }
    .nav-btn:disabled {
        opacity: 0.35;
    }
    body[data-theme="light"] .nav-btn {
        background: rgba(255, 255, 255, 0.8);
        color: #000;
        border-color: rgba(0, 0, 0, 0.5);
    }
    .pagination-bar {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: center;
        font-size: 0.85rem;
        gap: 0.6rem;
        padding-top: 0.6rem;
    }
    .pagination-meta {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        flex-wrap: wrap;
    }
    .pagination-controls {
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .pagination-controls .page-input,
    .pagination-bar select {
        width: 4.5rem;
        border-radius: 0.35rem;
        font-size: 0.85rem;
        text-align: center;
        background: transparent;
        color: inherit;
        border-color: var(--photo-border-color);
        border-width: 1px;
        border-style: solid;
    }
    .pagination-controls button {
        min-width: 2.25rem;
        padding: 0.15rem 0.35rem;
        border-radius: 0.35rem;
        background: transparent;
        color: inherit;
        border-color: var(--photo-border-color);
        font-size: 1rem;
    }
    .pagination-controls button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    .pagination-summary {
        font-size: 0.82rem;
        margin-left: 0.4rem;
        white-space: nowrap;
        color: inherit;
    }
    .table-striped tbody tr:nth-of-type(odd) {
        background-color: var(--photo-stripe-color);
    }
    tbody tr:hover {
        background-color: rgba(0, 0, 0, 0.04);
    }
    body[data-theme="dark"] tbody tr:hover {
        background-color: rgba(255, 255, 255, 0.06);
    }
</style>
<div class="table-shell">
    <p class="lead" id="loading-note">Paged loading: only render visible rows to keep large Photos.sqlite lists responsive.</p>
    <div class="table-wrapper">
        <table>
            <thead>
                <tr>
                    <th>Media</th>
                    <th>Filename</th>
                    <th>Directory</th>
                    <th>Timestamp</th>
                    <th>Timestamp Modification</th>
                    <th>Exif Creation/Changed</th>
                    <th>Possible Exif Offset</th>
                    <th>Same Timestamps?</th>
                    <th>Same Coordinates?</th>
                    <th>Latitude DB</th>
                    <th>Longitude DB</th>
                    <th>Latitude</th>
                    <th>Longitude</th>
                    <th>Exif</th>
                    <th>Bundle Creator</th>
                </tr>
            </thead>
            <tbody id="photos-body"></tbody>
        </table>
    </div>
    <div class="pagination-bar">
        <div class="pagination-meta">
            <label class="rows-label" for="page-size">Rows per page:</label>
            <select id="page-size">
                <option value="5">5</option>
                <option value="10" selected>10</option>
                <option value="20">20</option>
                <option value="50">50</option>
                <option value="all">All</option>
            </select>
            <span class="pagination-summary" id="page-summary">Showing 0 to 0 of 0 entries</span>
        </div>
        <div class="pagination-controls">
            <button id="first-page" aria-label="First page">«</button>
            <button id="prev-page" aria-label="Previous page">&lsaquo;</button>
            <span class="page-info" id="page-info">Page 0 of 0</span>
            <label class="sr-only" for="page-input">Go to page</label>
            <input id="page-input" class="page-input" type="number" min="1" value="1" aria-label="Go to page">
            <button id="next-page" aria-label="Next page">&rsaquo;</button>
            <button id="last-page" aria-label="Last page">»</button>
        </div>
    </div>
</div>
<div class="overlay" id="preview">
    <button type="button" class="close-btn" aria-label="Close preview">&times;</button>
    <img class="overlay-image" alt="Full preview">
    <video class="overlay-video" controls playsinline preload="metadata"></video>
    <div class="overlay-nav">
        <button type="button" id="nav-prev" class="nav-btn" aria-label="Previous item">&lsaquo;</button>
        <button type="button" id="nav-next" class="nav-btn" aria-label="Next item">&rsaquo;</button>
    </div>
</div>
<script type="application/json" id="data-json">__DATA_JSON__</script>
"""


def render_photo_script():
    return """
<script>
(function() {
    const spinner = document.getElementById('mySpinner');
    if (spinner) {
        spinner.remove();
    }

    const dataSource = document.getElementById('data-json');
    const data = dataSource ? JSON.parse(dataSource.textContent || '[]') : [];
    const tbody = document.getElementById('photos-body');
    const tableWrapper = document.querySelector('.table-wrapper');
    const loadingNote = document.getElementById('loading-note');
    const pageSizeSelect = document.getElementById('page-size');
    const prevButton = document.getElementById('prev-page');
    const nextButton = document.getElementById('next-page');
    const firstButton = document.getElementById('first-page');
    const lastButton = document.getElementById('last-page');
    const pageInput = document.getElementById('page-input');
    const pageInfo = document.getElementById('page-info');
    const pageSummary = document.getElementById('page-summary');
    const overlay = document.getElementById('preview');
    const previewImage = overlay ? overlay.querySelector('.overlay-image') : null;
    const previewVideo = overlay ? overlay.querySelector('.overlay-video') : null;
    const closeButton = overlay ? overlay.querySelector('.close-btn') : null;
    const prevNavButton = document.getElementById('nav-prev');
    const nextNavButton = document.getElementById('nav-next');

    const columns = [
        { name: 'Filename', type: 'string', align: 'left' },
        { name: 'Directory', type: 'string', align: 'left' },
        { name: 'Timestamp', type: 'datetime', align: 'left' },
        { name: 'Timestamp Modification', type: 'datetime', align: 'left' },
        { name: 'Exif Creation/Changed', type: 'datetime', align: 'left' },
        { name: 'Possible Exif Offset', type: 'string', align: 'center' },
        { name: 'Same Timestamps?', type: 'boolean', align: 'center' },
        { name: 'Same Coordinates?', type: 'boolean', align: 'center' },
        { name: 'Latitude DB', type: 'number', align: 'right' },
        { name: 'Longitude DB', type: 'number', align: 'right' },
        { name: 'Latitude', type: 'number', align: 'right' },
        { name: 'Longitude', type: 'number', align: 'right' },
        { name: 'Exif', type: 'multiline', align: 'left' },
        { name: 'Bundle Creator', type: 'string', align: 'left' }
    ];

    let currentPage = 1;
    let showAll = pageSizeSelect.value === 'all';
    let pageSize = showAll ? data.length : Number(pageSizeSelect.value) || 10;
    let sortColumn = null;
    let sortDirection = 1;
    const headerCells = document.querySelectorAll('.table-wrapper thead th');
    let isZoomed = false;

    const normalizeValue = value => (value || '').toString().trim().toLowerCase();
    const VIDEO_EXTENSIONS = /\\.(mp4|mov|m4v|avi|3gp|3g2|mkv|mpg|mpeg|wmv)$/i;
    const getMediaSource = entry => (entry && (entry.preview || entry.thumb)) || '';
    const isVideoEntry = entry => {
        const declared = (entry && entry.mediaType ? entry.mediaType : '').toLowerCase();
        if (declared.startsWith('video')) {
            return true;
        }
        const source = getMediaSource(entry).split('?')[0].toLowerCase();
        return VIDEO_EXTENSIONS.test(source);
    };
    const resolveMediaType = entry => (isVideoEntry(entry) ? 'video' : 'image');

    const isLegacyFieldOrder = fields => Array.isArray(fields) && fields.length >= 14 &&
        (fields[0] === 'True' || fields[0] === 'False' || fields[0] === '');
    const remapLegacyFields = fields => ([
        fields[6],  // Filename
        fields[5],  // Directory
        fields[3],  // Timestamp
        fields[4],  // Timestamp Modification
        fields[9],  // Exif Creation/Changed
        fields[1],  // Possible Exif Offset
        fields[0],  // Same Timestamps?
        fields[2],  // Same Coordinates?
        fields[7],  // Latitude DB
        fields[8],  // Longitude DB
        fields[10], // Latitude
        fields[11], // Longitude
        fields[12], // Exif
        fields[13]  // Bundle Creator
    ]);

    if (Array.isArray(data)) {
        data.forEach(entry => {
            if (entry && isLegacyFieldOrder(entry.fields)) {
                entry.fields = remapLegacyFields(entry.fields);
            }
        });
    }

    const getColumnMeta = index => columns[index] || { type: 'string', align: 'left' };

    const parseForSort = (value, type) => {
        if (value === null || value === undefined) {
            return null;
        }
        const str = value.toString().trim();
        if (!str) {
            return null;
        }
        if (type === 'number') {
            const num = Number(str);
            return Number.isNaN(num) ? null : num;
        }
        if (type === 'datetime') {
            const ts = Date.parse(str.replace(' ', 'T'));
            return Number.isNaN(ts) ? null : ts;
        }
        if (type === 'boolean') {
            const lowered = str.toLowerCase();
            if (lowered === 'true') return true;
            if (lowered === 'false') return false;
            return null;
        }
        return str.toLowerCase();
    };

    const formatForDisplay = (value, type) => {
        if (value === null || value === undefined) {
            return '';
        }
        if (type === 'number') {
            const num = Number(value);
            if (Number.isNaN(num)) {
                return value.toString();
            }
            return num.toFixed(6);
        }
        return value;
    };

    let currentPreviewIndex = null;

    const updateSortIndicators = activeIndex => {
        headerCells.forEach((cell, idx) => {
            cell.classList.remove('sorted-asc', 'sorted-desc');
            cell.setAttribute('aria-sort', 'none');
            if (idx === activeIndex && sortColumn !== null) {
                const asc = sortDirection === 1;
                cell.classList.add(asc ? 'sorted-asc' : 'sorted-desc');
                cell.setAttribute('aria-sort', asc ? 'ascending' : 'descending');
            }
        });
    };

    const updateNavControls = () => {
        if (!prevNavButton || !nextNavButton) {
            return;
        }
        prevNavButton.disabled = currentPreviewIndex === null || currentPreviewIndex <= 0;
        nextNavButton.disabled = currentPreviewIndex === null || currentPreviewIndex >= data.length - 1;
    };

    const resetPreviewMedia = () => {
        if (previewVideo) {
            previewVideo.pause();
            previewVideo.removeAttribute('src');
            previewVideo.load();
            previewVideo.style.display = 'none';
        }
        if (previewImage) {
            previewImage.src = '';
            previewImage.style.display = 'none';
        }
    };

    const showPreviewMedia = entry => {
        const source = getMediaSource(entry);
        if (!source || (!previewImage && !previewVideo)) {
            resetPreviewMedia();
            return;
        }
        const isVideo = isVideoEntry(entry);
        resetPreviewMedia();
        isZoomed = false;
        if (overlay) {
            overlay.classList.remove('zoomed');
        }
        if (isVideo && previewVideo) {
            previewVideo.style.display = 'block';
            previewVideo.src = source;
            previewVideo.load();
            previewVideo.play().catch(() => {});
        } else if (previewImage) {
            previewImage.src = source;
            previewImage.style.display = 'block';
        }
    };

    const openPreview = index => {
        if (!overlay) {
            return;
        }
        if (!Number.isInteger(index) || index < 0 || index >= data.length) {
            return;
        }
        const targetPage = showAll ? 1 : Math.floor(index / pageSize) + 1;
        const needsRender = targetPage !== currentPage && !showAll;
        currentPage = targetPage;
        if (needsRender) {
            renderPage();
        }
        const entry = data[index];
        if (!entry) {
            return;
        }
        showPreviewMedia(entry);
        currentPreviewIndex = index;
        updateNavControls();
        overlay.classList.add('show');
    };

    const closePreview = () => {
        if (!overlay) {
            return;
        }
        overlay.classList.remove('show');
        resetPreviewMedia();
        currentPreviewIndex = null;
        updateNavControls();
    };

    const sortEntries = () => {
        if (sortColumn === null) {
            return;
        }
        const meta = getColumnMeta(sortColumn);
        data.sort((a, b) => {
            const valA = parseForSort(a.fields[sortColumn], meta.type);
            const valB = parseForSort(b.fields[sortColumn], meta.type);
            if (valA === null && valB === null) return 0;
            if (valA === null) return 1;
            if (valB === null) return -1;
            if (valA < valB) return -sortDirection;
            if (valA > valB) return sortDirection;
            return 0;
        });
    };

    headerCells.forEach((header, idx) => {
        if (idx === 0) {
            return;
        }
        header.classList.add('sortable');
        header.addEventListener('click', () => {
            const fieldIndex = idx - 1;
            if (sortColumn === fieldIndex) {
                sortDirection = -sortDirection;
            } else {
                sortDirection = 1;
                sortColumn = fieldIndex;
            }
            sortEntries();
            updateSortIndicators(idx);
            currentPage = 1;
            renderPage();
        });
    });

    const createRow = (entry, rowIndex) => {
        const tr = document.createElement('tr');
        const thumbTd = document.createElement('td');
        const source = getMediaSource(entry);
        if (source) {
            const wrapper = document.createElement('div');
            wrapper.className = 'media-thumb';
            const fullSource = entry.preview || entry.thumb || source;
            if (resolveMediaType(entry) === 'video') {
                const video = document.createElement('video');
                video.src = source;
                video.width = 180;
                video.height = 120;
                video.setAttribute('preload', 'metadata');
                video.setAttribute('controls', 'controls');
                video.setAttribute('playsinline', 'playsinline');
                video.dataset.full = fullSource;
                video.dataset.index = rowIndex;
                wrapper.appendChild(video);
            } else {
                const img = document.createElement('img');
                img.src = source;
                img.loading = 'lazy';
                img.alt = 'thumbnail';
                img.width = 180;
                img.height = 120;
                img.dataset.full = fullSource;
                img.dataset.index = rowIndex;
                wrapper.appendChild(img);
            }
            thumbTd.appendChild(wrapper);
        } else {
            thumbTd.innerHTML = '<span class="no-thumb">No thumbnail</span>';
        }
        tr.appendChild(thumbTd);
        entry.fields.forEach((text, idx) => {
            const td = document.createElement('td');
            const meta = getColumnMeta(idx);
            const displayValue = formatForDisplay(text, meta.type);
            td.textContent = displayValue;
            td.style.textAlign = meta.align || 'left';
            if (meta.type === 'multiline') {
                td.style.whiteSpace = 'pre-wrap';
            }
            tr.appendChild(td);
        });
        return tr;
    };

    const attachPreviewHandlers = () => {
        if (!tbody || !overlay) {
            return;
        }
        tbody.querySelectorAll('.media-thumb [data-index]').forEach(mediaEl => {
            const index = Number(mediaEl.dataset.index);
            if (Number.isNaN(index)) {
                return;
            }
            mediaEl.style.cursor = 'pointer';
            mediaEl.addEventListener('click', () => openPreview(index));
        });
    };

    const renderPage = () => {
        if (!tbody) {
            return;
        }
        if (loadingNote) {
            loadingNote.style.display = data.length ? 'none' : 'block';
        }
        const totalPages = showAll ? 1 : Math.max(1, Math.ceil(data.length / pageSize));
        if (currentPage > totalPages) {
            currentPage = totalPages;
        }
        const start = showAll ? 0 : (currentPage - 1) * pageSize;
        const end = showAll ? data.length : Math.min(data.length, start + pageSize);
        const fragment = document.createDocumentFragment();
        const batch = data.slice(start, end);
        tbody.innerHTML = '';
        batch.forEach((entry, index) => fragment.appendChild(createRow(entry, start + index)));
        tbody.appendChild(fragment);
        if (pageInfo) {
            pageInfo.textContent = showAll ? `Page 1 of 1` : `Page ${currentPage} of ${totalPages}`;
        }
        if (pageSummary) {
            const totalEntries = data.length;
            const entryStart = totalEntries ? (showAll ? 1 : start + 1) : 0;
            const entryEnd = totalEntries ? (showAll ? totalEntries : end) : 0;
            pageSummary.textContent = `Showing ${entryStart} to ${entryEnd} of ${totalEntries} entries`;
        }
        if (prevButton) {
            prevButton.disabled = showAll || currentPage <= 1;
        }
        if (nextButton) {
            nextButton.disabled = showAll || currentPage >= totalPages;
        }
        if (firstButton) {
            firstButton.disabled = showAll || currentPage <= 1;
        }
        if (lastButton) {
            lastButton.disabled = showAll || currentPage >= totalPages;
        }
        if (pageInput) {
            pageInput.max = totalPages;
            pageInput.value = showAll ? 1 : currentPage;
        }
        attachPreviewHandlers();
        if (tableWrapper) {
            tableWrapper.scrollTo({ top: 0, behavior: 'auto' });
        }
        updateNavControls();
    };

    if (closeButton && overlay) {
        closeButton.addEventListener('click', () => closePreview());
        overlay.addEventListener('click', event => {
            if (event.target === overlay) {
                closePreview();
            }
        });
    }

    if (prevNavButton) {
        prevNavButton.addEventListener('click', () => {
            if (currentPreviewIndex > 0) {
                openPreview(currentPreviewIndex - 1);
            }
        });
    }

    if (nextNavButton) {
        nextNavButton.addEventListener('click', () => {
            if (currentPreviewIndex < data.length - 1) {
                openPreview(currentPreviewIndex + 1);
            }
        });
    }

    if (pageSizeSelect) {
        pageSizeSelect.addEventListener('change', () => {
            showAll = pageSizeSelect.value === 'all';
            pageSize = showAll ? data.length : Number(pageSizeSelect.value) || data.length;
            currentPage = 1;
            renderPage();
        });
    }

    if (firstButton) {
        firstButton.addEventListener('click', () => {
            if (!showAll && currentPage > 1) {
                currentPage = 1;
                renderPage();
            }
        });
    }

    if (prevButton) {
        prevButton.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage -= 1;
                renderPage();
            }
        });
    }

    if (lastButton) {
        lastButton.addEventListener('click', () => {
            const totalPages = showAll ? 1 : Math.max(1, Math.ceil(data.length / pageSize));
            if (!showAll && currentPage < totalPages) {
                currentPage = totalPages;
                renderPage();
            }
        });
    }

    if (nextButton) {
        nextButton.addEventListener('click', () => {
            const totalPages = showAll ? 1 : Math.max(1, Math.ceil(data.length / pageSize));
            if (currentPage < totalPages) {
                currentPage += 1;
                renderPage();
            }
        });
    }

    if (pageInput) {
        pageInput.addEventListener('change', () => {
            if (showAll) {
                if (pageInput.value !== "1") {
                    pageInput.value = "1";
                }
                return;
            }
            const totalPages = Math.max(1, Math.ceil(data.length / pageSize));
            let target = Number(pageInput.value);
            if (!Number.isInteger(target) || target < 1) {
                target = 1;
            }
            if (target > totalPages) {
                target = totalPages;
            }
            if (target !== currentPage) {
                currentPage = target;
                renderPage();
            }
        });
    }

    if (previewImage && overlay) {
        previewImage.addEventListener('click', () => {
            isZoomed = !isZoomed;
            overlay.classList.toggle('zoomed', isZoomed);
            if (isZoomed) {
                overlay.scrollTo({ top: 0, left: 0 });
            }
        });
        overlay.addEventListener('wheel', event => {
            if (!isZoomed) {
                return;
            }
            event.preventDefault();
            overlay.scrollTop += event.deltaY;
            overlay.scrollLeft += event.deltaX;
        }, { passive: false });
    }

    renderPage();
})();
</script>
"""

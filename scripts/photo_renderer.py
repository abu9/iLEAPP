# coding: utf-8
photo_HTML = """
<style>
    .table-shell {
        background: #111;
        border-radius: 16px;
        padding: 1rem;
        color: #fff;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .table-shell .lead {
        font-size: 0.95rem;
        color: #dcdcdc;
        margin-bottom: 0.5rem;
    }
    .table-wrapper {
        max-height: 70vh;
        overflow: auto;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    table {
        width: 100%;
        min-width: 1500px;
        border-collapse: collapse;
        table-layout: auto;
        font-size: 0.85rem;
        color: #fff;
    }
    th, td {
        padding: 0.6rem 0.8rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        vertical-align: middle;
        word-break: break-word;
    }
    th {
        background: #1f1f1f;
        position: sticky;
        top: 0;
        z-index: 2;
        font-weight: 600;
    }
    th:first-child,
    td:first-child {
        position: sticky;
        left: 0;
        z-index: 3;
        background: #1f1f1f;
        box-shadow: 2px 0 12px rgba(0, 0, 0, 0.55);
    }
    .media-thumb {
        display: flex;
        justify-content: center;
    }
    .media-thumb img,
    .media-thumb video {
        border-radius: 10px;
        max-width: 180px;
        max-height: 120px;
        object-fit: cover;
        background: #222;
        transition: transform 0.2s ease;
        outline: 2px solid transparent;
    }
    .media-thumb video {
        background: #000;
    }
    .media-thumb img:hover,
    .media-thumb video:hover {
        transform: scale(1.03);
        outline-color: rgba(255, 255, 255, 0.4);
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
    }
    .overlay.show {
        opacity: 1;
        visibility: visible;
    }
    .overlay img,
    .overlay video {
        max-width: 90vw;
        max-height: 90vh;
        border-radius: 12px;
        box-shadow: 0 0 30px rgba(0, 0, 0, 0.6);
        object-fit: contain;
    }
    .overlay video {
        display: none;
        background: #000;
    }
    .overlay .close-btn {
        position: absolute;
        top: 1rem;
        right: 1rem;
        width: 44px;
        height: 44px;
        border-radius: 50%;
        border: none;
        background: rgba(20, 20, 20, 0.85);
        color: #fff;
        font-size: 1.4rem;
        cursor: pointer;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
    }
    .overlay-nav {
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 1rem;
        pointer-events: none;
    }
    .nav-btn {
        pointer-events: auto;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        border: none;
        background: rgba(20, 20, 20, 0.75);
        color: #fff;
        font-size: 1.8rem;
        cursor: pointer;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
        transition: transform 0.2s ease, background 0.2s ease;
    }
    .nav-btn:disabled {
        opacity: 0.35;
        cursor: not-allowed;
    }
    .nav-btn:not(:disabled):hover {
        transform: scale(1.05);
        background: rgba(40, 40, 40, 0.85);
    }
    .pagination-bar {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: center;
        font-size: 0.85rem;
        color: #c8c8c8;
        gap: 0.6rem;
        padding-top: 0.6rem;
    }
    .pagination-meta {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        flex-wrap: wrap;
    }
    .pagination-meta .rows-label {
        font-weight: 500;
    }
    .pagination-bar select {
        background: #222;
        color: #fff;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 6px;
        padding: 0.2rem 0.6rem;
        cursor: pointer;
        outline: none;
    }
    .pagination-bar button {
        background: #2c2c2c;
        color: #fff;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 6px;
        padding: 0.35rem 0.8rem;
        cursor: pointer;
        transition: background 0.2s ease;
    }
    .pagination-bar button:disabled {
        opacity: 0.4;
        cursor: not-allowed;
    }
    .pagination-bar button:not(:disabled):hover {
        background: #414141;
    }
    .pagination-controls {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .pagination-controls .page-input {
        width: 4.5rem;
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.25);
        background: #1a1a1a;
        color: #fff;
        padding: 0 0.4rem;
        font-size: 0.85rem;
        text-align: center;
    }
    .pagination-summary {
        font-size: 0.82rem;
        color: #d0d0d0;
        margin-left: 0.4rem;
        white-space: nowrap;
    }
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }
    .page-info {
        min-width: 110px;
        text-align: center;
        font-weight: 500;
    }
    .sortable {
        cursor: pointer;
    }
    .sortable::after {
        content: "^v";
        font-size: 0.7rem;
        margin-left: 0.35rem;
        opacity: 0.4;
    }
    .sorted-asc::after {
        content: "^";
        opacity: 1;
    }
    .sorted-desc::after {
        content: "v";
        opacity: 1;
    }
    .no-thumb {
        font-size: 0.75rem;
        color: #aaa;
    }
    @media (max-width: 900px) {
        table {
            min-width: 1200px;
        }
    }
</style>
<div class="table-shell">
    <p class="lead" id="loading-note">Paged loading: only render visible rows to keep large Photos.sqlite lists responsive.</p>
    <div class="table-wrapper">
        <table>
            <thead>
                <tr>
                    <th>Media</th>
                    <th>Same Timestamps?</th>
                    <th>Possible Exif Offset</th>
                    <th>Same Coordinates?</th>
                    <th>Timestamp</th>
                    <th>Timestamp Modification</th>
                    <th>Directory</th>
                    <th>Filename</th>
                    <th>Latitude DB</th>
                    <th>Longitude DB</th>
                    <th>Exif Creation/Changed</th>
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

    let currentPage = 1;
    let showAll = pageSizeSelect.value === 'all';
    let pageSize = showAll ? data.length : Number(pageSizeSelect.value) || 10;
    let sortColumn = null;
    let sortDirection = 1;
    const headerCells = document.querySelectorAll('.table-wrapper thead th');

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

    let currentPreviewIndex = null;

    const updateSortIndicators = activeIndex => {
        headerCells.forEach((cell, idx) => {
            cell.classList.remove('sorted-asc', 'sorted-desc');
            if (idx === activeIndex && sortColumn !== null) {
                cell.classList.add(sortDirection === 1 ? 'sorted-asc' : 'sorted-desc');
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
        data.sort((a, b) => {
            const valA = normalizeValue(a.fields[sortColumn]);
            const valB = normalizeValue(b.fields[sortColumn]);
            if (valA < valB) {
                return -sortDirection;
            }
            if (valA > valB) {
                return sortDirection;
            }
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
        entry.fields.forEach(text => {
            const td = document.createElement('td');
            td.innerHTML = text || '';
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

    renderPage();
})();
</script>
"""

// ============================================
// STATE
// ============================================
const STATE = {
    currentFileId: null,
    currentResults: null,
    versionHistory: [],
    currentVersion: 0
};

// ============================================
// DEMO DATA
// ============================================
const DEMO_DATA = {
    file_id: "demo-mode-00000000-0000-0000-0000-000000000000",
    filename: "sample_tz.docx",
    original_score: 58,
    score_breakdown: {
        section_completeness: 20,
        strategic_references: 8,
        quantitative_results: 12,
        budget_breakdown: 10,
        logical_consistency: 5,
        language_clarity: 3
    },
    language: "russian",
    issues: [
        {
            section: "Раздел 3: Стратегические документы",
            severity: "high",
            description: "Перечисляются только названия стратегических документов без конкретных номеров пунктов",
            original_text: "Государственная программа развития ИКТ\nНациональный стратегический план развития",
            suggested_fix: "Государственная программа развития ИКТ на 2022-2026 годы, п. 2.3 «Развитие научных исследований»\nНациональный стратегический план развития РК на 2025-2029 годы, раздел IV, п. 18"
        },
        {
            section: "Раздел 4.1: Прямые результаты",
            severity: "high",
            description: "Количество публикаций не указано, отсутствует информация о квартилях WoS/Scopus",
            original_text: "Будут опубликованы научные статьи в рецензируемых журналах",
            suggested_fix: "Минимум 3 статьи в журналах WoS квартиля Q2 или выше, минимум 2 статьи в Scopus с CiteScore ≥ 50"
        },
        {
            section: "Раздел 5: Финансирование",
            severity: "medium",
            description: "Указана общая сумма, но отсутствует разбивка по годам выполнения программы",
            original_text: "Общая сумма: 5 000 тыс. тенге",
            suggested_fix: "Общая сумма: 5 000 тыс. тенге\n2024 год: 1 500 тыс. тенге\n2025 год: 1 800 тыс. тенге\n2026 год: 1 700 тыс. тенге"
        },
        {
            section: "Раздел 2.2: Задачи",
            severity: "low",
            description: "Задачи сформулированы слишком общо, без конкретных измеримых показателей",
            original_text: "Провести исследования\nРазработать технологии",
            suggested_fix: "Провести экспериментальные исследования и подготовить 2 научных публикации\nРазработать прототип системы с производительностью не менее 10 000 оп/с"
        }
    ],
    suggestions: [
        "Добавьте конкретные номера пунктов для каждого стратегического документа в Разделе 3",
        "Уточните количество публикаций с базами индексирования и квартилями",
        "Разбейте общий бюджет по годам в Разделе 5",
        "Переформулируйте задачи по SMART-критериям",
        "В Разделе 4.2 добавьте экономический, экологический и социальный эффект",
        "Укажите конкретных целевых потребителей результатов программы"
    ],
    corrected_sections: {},
    summary: "Техническое задание охватывает основные разделы, однако имеет значительные пробелы в конкретизации. Наиболее критичные проблемы: отсутствие ссылок на конкретные пункты стратегических документов, неопределённые показатели результатов и отсутствие разбивки бюджета по годам. После устранения выявленных проблем оценка может быть повышена до 85–90 баллов."
};

// ============================================
// LOADING HINTS
// ============================================
const LOADING_HINTS = [
    "Проверка структуры ТЗ...",
    "Анализ ссылок на документы...",
    "Оценка количественных показателей...",
    "Проверка бюджетной разбивки...",
    "Оценка логической согласованности...",
    "Формирование рекомендаций...",
    "Расчёт итогового балла..."
];

let hintInterval = null;

// ============================================
// DOM REFS
// ============================================
const uploadZone    = document.getElementById('uploadZone');
const fileInput     = document.getElementById('fileInput');
const browseBtn     = document.getElementById('browseBtn');
const uploadPage    = document.getElementById('uploadPage');
const resultsPage   = document.getElementById('resultsPage');
const historyPage   = document.getElementById('historyPage');
const loadingOverlay = document.getElementById('loadingOverlay');
const toastContainer = document.getElementById('toastContainer');
const navLinks      = document.querySelectorAll('.nav-link');
const applyFixesBtn = document.getElementById('applyFixesBtn');
const resetBtn      = document.getElementById('resetBtn');
const downloadCorrectedBtn = document.getElementById('downloadCorrectedBtn');
const exportExcelBtn = document.getElementById('exportExcelBtn');
const exportAllBtn  = document.getElementById('exportAllBtn');
const pageTitle     = document.getElementById('pageTitle');
const infoBtn       = document.getElementById('infoBtn');
const criteriaModal = document.getElementById('criteriaModal');
const closeCriteriaBtn = document.getElementById('closeCriteriaBtn');
const scoreComparison  = document.getElementById('scoreComparison');
const demoBtn       = document.getElementById('demoBtn');
const statusDot     = document.getElementById('statusDot');

// ============================================
// INIT
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    checkServerHealth();
    initDragDrop();
    setupNavigation();
    setupEventListeners();
    setupModalListeners();
    loadHistory();
    setupDemoMode();
});

// ============================================
// DRAG AND DROP
// ============================================
function initDragDrop() {
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) handleFileUpload(e.dataTransfer.files[0]);
    });

    uploadZone.addEventListener('click', () => fileInput.click());

    browseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) handleFileUpload(e.target.files[0]);
    });
}

// ============================================
// FILE UPLOAD
// ============================================
function handleFileUpload(file) {
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['docx', 'pdf'].includes(ext)) {
        showToast('Поддерживаются только форматы .docx и .pdf', 'error');
        return;
    }
    if (file.size > 10 * 1024 * 1024) {
        showToast('Размер файла не должен превышать 10 MB', 'error');
        return;
    }
    analyzeFile(file);
}

// ============================================
// API CALLS
// ============================================
async function analyzeFile(file) {
    showLoading('ИИ анализирует документ');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/analyze', { method: 'POST', body: formData });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Ошибка при анализе документа');
        }

        const data = await response.json();
        STATE.currentFileId = data.file_id;
        STATE.currentResults = data;
        STATE.versionHistory = [{
            version: 1,
            score: data.original_score,
            timestamp: new Date().toLocaleString('ru-RU'),
            changes: [],
            resultsSnapshot: JSON.parse(JSON.stringify(data))
        }];
        STATE.currentVersion = 1;

        displayResults(data);
        updateLanguageBadge(data.language);
        showToast('Документ успешно проанализирован', 'success');
    } catch (error) {
        showToast(`Ошибка: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

async function applySelectedFixes() {
    const checked = document.querySelectorAll('.issue-checkbox:checked');
    const issuesToFix = Array.from(checked).map(cb => parseInt(cb.dataset.issueIndex));

    if (issuesToFix.length === 0) {
        showToast('Выберите хотя бы одну проблему для исправления', 'warning');
        return;
    }

    showLoading('ИИ применяет исправления');

    try {
        const response = await fetch('/api/apply-fix', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_id: STATE.currentFileId, issues_to_fix: issuesToFix, custom_instruction: '' })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Ошибка при применении исправлений');
        }

        const data = await response.json();
        const oldScore = STATE.currentResults.original_score;
        STATE.currentResults.original_score = data.new_score;
        STATE.currentVersion += 1;
        STATE.versionHistory.push({
            version: STATE.currentVersion,
            score: data.new_score,
            timestamp: new Date().toLocaleString('ru-RU'),
            changes: data.changes_made,
            resultsSnapshot: JSON.parse(JSON.stringify(STATE.currentResults))
        });

        downloadCorrectedBtn.disabled = false;
        downloadCorrectedBtn.onclick = () => downloadFile(data.download_url);

        showScoreComparison(oldScore, data.new_score);
        animateScoreGaugeFromTo(oldScore, data.new_score);
        renderVersionHistory();
        document.querySelectorAll('.issue-checkbox').forEach(cb => cb.checked = false);
        showToast('Исправления успешно применены', 'success');
    } catch (error) {
        showToast(`Ошибка: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

async function downloadFile(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Ошибка при скачивании файла');
        const blob = await response.blob();
        const filename = url.split('/').pop() || 'corrected_document.docx';
        const a = Object.assign(document.createElement('a'), {
            href: window.URL.createObjectURL(blob),
            download: filename
        });
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(a.href);
        document.body.removeChild(a);
        showToast('Файл успешно скачан', 'success');
    } catch (error) {
        showToast(`Ошибка при скачивании: ${error.message}`, 'error');
    }
}

async function downloadExcel() {
    try {
        const response = await fetch('/api/download-excel');
        if (!response.ok) throw new Error('Ошибка при скачивании');
        const blob = await response.blob();
        const a = Object.assign(document.createElement('a'), {
            href: window.URL.createObjectURL(blob),
            download: 'tz_scores.xlsx'
        });
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(a.href);
        document.body.removeChild(a);
        showToast('Excel файл скачан', 'success');
    } catch (error) {
        showToast(`Ошибка: ${error.message}`, 'error');
    }
}

async function loadHistory() {
    try {
        const response = await fetch('/api/records');
        if (!response.ok) throw new Error('Ошибка загрузки');
        const data = await response.json();
        renderHistoryTable(data.records);
    } catch (error) {
        console.error('History load error:', error);
    }
}

// ============================================
// DISPLAY RESULTS
// ============================================
function displayResults(data) {
    document.getElementById('resultFilename').textContent = data.filename;

    const langMap   = { russian: 'РУС', kazakh: 'КАЗ' };
    const langText  = { russian: 'Русский язык', kazakh: 'Қазақ тілі' };
    document.getElementById('resultLanguageBadge').textContent = langMap[data.language] || 'РУС';
    document.getElementById('resultLanguageText').textContent  = langText[data.language] || 'Русский язык';

    downloadCorrectedBtn.disabled = true;
    downloadCorrectedBtn.onclick  = null;
    scoreComparison.classList.add('hidden');

    animateScoreGauge(data.original_score);
    renderScoreBreakdown(data.score_breakdown);
    renderIssues(data.issues);
    renderSuggestionsAnimated(data.suggestions);
    renderSummaryAnimated(data.summary);
    renderVersionHistory();

    showPage('results');
}

// ============================================
// SCORE GAUGE ANIMATION
// ============================================
function animateScoreGauge(score) {
    const fg = document.getElementById('gaugeForeground');
    const num = document.getElementById('scoreNumber');
    const circ = 2 * Math.PI * 80;

    setGaugeColor(fg, score);
    num.textContent = '0';
    fg.style.strokeDasharray = `0 ${circ}`;

    animateValue(0, score, 1000, (v) => {
        num.textContent = v;
        fg.style.strokeDasharray = `${(v / 100) * circ} ${circ}`;
    });
}

function animateScoreGaugeFromTo(from, to) {
    const fg = document.getElementById('gaugeForeground');
    const num = document.getElementById('scoreNumber');
    const circ = 2 * Math.PI * 80;

    setGaugeColor(fg, to);
    animateValue(from, to, 1000, (v) => {
        num.textContent = v;
        fg.style.strokeDasharray = `${(v / 100) * circ} ${circ}`;
    });
}

function setGaugeColor(el, score) {
    el.className = 'gauge-fg ' + (score < 50 ? 'score-low' : score < 75 ? 'score-mid' : 'score-high');
}

function animateValue(from, to, duration, callback) {
    const start = performance.now();
    function step(now) {
        const p = Math.min((now - start) / duration, 1);
        const ease = 1 - Math.pow(1 - p, 3);
        callback(Math.round(from + ease * (to - from)));
        if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
}

// ============================================
// SCORE BREAKDOWN
// ============================================
function renderScoreBreakdown(breakdown) {
    const container = document.getElementById('breakdownBars');
    container.innerHTML = '';

    const cats = [
        { key: 'section_completeness',  label: 'Полнота разделов',           max: 25 },
        { key: 'strategic_references',  label: 'Ссылки на документы',        max: 20 },
        { key: 'quantitative_results',  label: 'Количественные результаты',  max: 20 },
        { key: 'budget_breakdown',      label: 'Разбор бюджета',             max: 15 },
        { key: 'logical_consistency',   label: 'Логическая согласованность', max: 10 },
        { key: 'language_clarity',      label: 'Ясность языка',             max: 10 }
    ];

    cats.forEach((cat, i) => {
        const score = breakdown[cat.key] || 0;
        const pct = (score / cat.max) * 100;
        const bar = document.createElement('div');
        bar.className = 'breakdown-bar';
        bar.innerHTML = `
            <div class="breakdown-label">
                <span>${cat.label}</span>
                <span>${score}/${cat.max}</span>
            </div>
            <div class="breakdown-track">
                <div class="breakdown-fill" data-width="${pct}"></div>
            </div>
        `;
        container.appendChild(bar);

        // Animate bar with stagger
        setTimeout(() => {
            bar.querySelector('.breakdown-fill').style.width = `${pct}%`;
        }, 100 + i * 80);
    });
}

// ============================================
// ISSUES
// ============================================
function renderIssues(issues) {
    const container = document.getElementById('issuesList');
    const countEl   = document.getElementById('issuesCount');
    container.innerHTML = '';

    if (issues.length === 0) {
        countEl.textContent = '';
        container.innerHTML = '<p style="color:var(--success);font-weight:600;padding:8px 0;">Проблемы не обнаружены!</p>';
        return;
    }

    countEl.textContent = issues.length;

    const labelMap = { high: 'ВЫСОКАЯ', medium: 'СРЕДНЯЯ', low: 'НИЗКАЯ' };

    issues.forEach((issue, index) => {
        const card = document.createElement('div');
        card.className = `issue-card severity-${issue.severity}`;
        card.innerHTML = `
            <div class="issue-header">
                <div class="issue-header-left">
                    <input type="checkbox" class="issue-checkbox" data-issue-index="${index}">
                    <span class="issue-section-name">${escapeHtml(issue.section)}</span>
                    <span class="severity-badge ${issue.severity}">${labelMap[issue.severity] || issue.severity}</span>
                </div>
                <svg class="issue-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                    <polyline points="9 18 15 12 9 6"/>
                </svg>
            </div>
            <div class="issue-description">${escapeHtml(issue.description)}</div>
            <div class="issue-details">
                <div>
                    <div class="issue-block-label">Проблемный текст</div>
                    <div class="code-block">${escapeHtml(issue.original_text)}</div>
                </div>
                <div>
                    <div class="issue-block-label">Предложенное исправление</div>
                    <div class="fix-block">${escapeHtml(issue.suggested_fix)}</div>
                </div>
            </div>
        `;

        // Toggle expand on card click (but not checkbox)
        card.addEventListener('click', (e) => {
            if (e.target.classList.contains('issue-checkbox')) return;
            card.classList.toggle('expanded');
        });

        container.appendChild(card);
    });
}

// ============================================
// TYPEWRITER ANIMATIONS
// ============================================
function typewriterText(el, text, speed = 18) {
    return new Promise(resolve => {
        el.textContent = '';
        el.classList.add('tw-cursor');
        let i = 0;
        const timer = setInterval(() => {
            el.textContent += text[i];
            i++;
            if (i >= text.length) {
                clearInterval(timer);
                el.classList.remove('tw-cursor');
                resolve();
            }
        }, speed);
    });
}

function renderSummaryAnimated(text) {
    const el = document.getElementById('summaryText');
    el.textContent = '';
    // Small delay so page transition finishes first
    setTimeout(() => typewriterText(el, text, 12), 600);
}

function renderSuggestionsAnimated(suggestions) {
    const container = document.getElementById('suggestionsList');
    container.innerHTML = '';

    suggestions.forEach((text, i) => {
        const li = document.createElement('li');
        li.style.opacity = '0';
        container.appendChild(li);

        setTimeout(async () => {
            li.style.transition = 'opacity 0.3s';
            li.style.opacity = '1';
            await typewriterText(li, text, 10);
        }, 800 + i * 400);
    });
}

// ============================================
// HISTORY TABLE
// ============================================
function renderHistoryTable(records) {
    const tbody = document.getElementById('recordsTableBody');
    tbody.innerHTML = '';

    if (!records || records.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--text-muted);padding:32px;">История пуста</td></tr>`;
        return;
    }

    records.forEach(record => {
        const orig = record.original_score;
        const corr = record.corrected_score;
        const improvement = corr != null ? corr - orig : null;

        const pillClass = orig >= 75 ? 'high' : orig >= 50 ? 'medium' : 'low';

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${escapeHtml(record.filename)}</td>
            <td>${record.language === 'russian' ? '🇷🇺 Русский' : '🇰🇿 Қазақша'}</td>
            <td><span class="score-pill ${pillClass}">${orig}</span></td>
            <td>${corr != null ? corr : '—'}</td>
            <td style="color:${improvement > 0 ? 'var(--success)' : 'var(--text-muted)'}">
                ${improvement != null ? (improvement > 0 ? '+' : '') + improvement : '—'}
            </td>
            <td>${record.timestamp}</td>
        `;
        tbody.appendChild(tr);
    });
}

// ============================================
// VERSION HISTORY
// ============================================
function renderVersionHistory() {
    const container = document.getElementById('versionHistory');

    if (STATE.versionHistory.length === 0) {
        container.innerHTML = '';
        return;
    }

    let html = '<div class="version-history-inner"><div class="version-history-title">История версий</div><div class="version-timeline">';

    STATE.versionHistory.forEach((v, i) => {
        const isLatest = i === STATE.versionHistory.length - 1;
        const improvement = i > 0 ? v.score - STATE.versionHistory[i - 1].score : null;
        const badgeHtml = improvement > 0
            ? `<div class="version-badge">+${improvement} баллов</div>`
            : '';
        const restoreHtml = !isLatest
            ? `<button class="version-restore-btn" onclick="restoreVersion(${i})">Восстановить</button>`
            : '';

        html += `
            <div class="version-item ${isLatest ? 'current' : ''}">
                <div class="version-num">Версия ${v.version}${isLatest ? ' • текущая' : ''}</div>
                <div class="version-score">${v.score}<span style="font-size:14px;font-weight:400;color:var(--text-muted)">/100</span></div>
                <div class="version-time">${v.timestamp}</div>
                ${badgeHtml}
                ${restoreHtml}
            </div>
        `;
    });

    html += '</div></div>';
    container.innerHTML = html;
}

function restoreVersion(idx) {
    const v = STATE.versionHistory[idx];
    STATE.currentResults = JSON.parse(JSON.stringify(v.resultsSnapshot));
    STATE.currentVersion = v.version;

    animateScoreGauge(v.score);
    renderScoreBreakdown(v.resultsSnapshot.score_breakdown);
    renderIssues(v.resultsSnapshot.issues);
    renderSuggestionsAnimated(v.resultsSnapshot.suggestions);
    renderSummaryAnimated(v.resultsSnapshot.summary);
    scoreComparison.classList.add('hidden');
    renderVersionHistory();
    showToast(`Восстановлена версия ${v.version}`, 'info');
}

// ============================================
// SCORE COMPARISON
// ============================================
function showScoreComparison(oldScore, newScore) {
    document.getElementById('comparisonBefore').textContent = oldScore;
    document.getElementById('comparisonAfter').textContent  = newScore;
    const diff = newScore - oldScore;
    document.getElementById('comparisonImprovement').textContent = (diff > 0 ? '+' : '') + diff;
    scoreComparison.classList.remove('hidden');
}

// ============================================
// LANGUAGE BADGE
// ============================================
function updateLanguageBadge(language) {
    const badges = { russian: '🇷🇺 РУС', kazakh: '🇰🇿 КАЗ' };
    document.getElementById('languageBadge').textContent = badges[language] || '🇷🇺 РУС';
}

// ============================================
// NAVIGATION
// ============================================
function showPage(pageName) {
    uploadPage.classList.add('hidden');
    resultsPage.classList.add('hidden');
    historyPage.classList.add('hidden');
    navLinks.forEach(l => l.classList.remove('active'));

    if (pageName === 'upload') {
        uploadPage.classList.remove('hidden');
        pageTitle.textContent = 'Анализ ТЗ';
        document.querySelector('[data-page="upload"]')?.classList.add('active');
    } else if (pageName === 'results') {
        resultsPage.classList.remove('hidden');
        pageTitle.textContent = 'Результаты анализа';
    } else if (pageName === 'history') {
        historyPage.classList.remove('hidden');
        pageTitle.textContent = 'История оценок';
        document.querySelector('[data-page="history"]')?.classList.add('active');
        loadHistory();
    }
}

function setupNavigation() {
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            showPage(link.dataset.page);
        });
    });
}

// ============================================
// LOADING
// ============================================
function showLoading(title = 'ИИ анализирует документ') {
    document.getElementById('loadingTitle').textContent = title;
    loadingOverlay.classList.remove('hidden');

    let hintIdx = 0;
    const hintEl = document.getElementById('loadingHint');
    hintEl.textContent = LOADING_HINTS[0];

    hintInterval = setInterval(() => {
        hintIdx = (hintIdx + 1) % LOADING_HINTS.length;
        hintEl.style.opacity = '0';
        setTimeout(() => {
            hintEl.textContent = LOADING_HINTS[hintIdx];
            hintEl.style.opacity = '1';
        }, 300);
    }, 2500);
}

function hideLoading() {
    clearInterval(hintInterval);
    hintInterval = null;
    loadingOverlay.classList.add('hidden');
}

// ============================================
// TOASTS
// ============================================
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'toastOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ============================================
// EVENT LISTENERS
// ============================================
function setupEventListeners() {
    applyFixesBtn.addEventListener('click', applySelectedFixes);

    resetBtn.addEventListener('click', () => {
        showPage('upload');
        fileInput.value = '';
        STATE.currentFileId = null;
        STATE.currentResults = null;
        STATE.versionHistory = [];
        STATE.currentVersion = 0;
        scoreComparison.classList.add('hidden');
    });

    exportExcelBtn.addEventListener('click', downloadExcel);
    exportAllBtn.addEventListener('click', downloadExcel);
}

function setupDemoMode() {
    if (!demoBtn) return;
    demoBtn.addEventListener('click', () => {
        STATE.currentFileId = DEMO_DATA.file_id;
        STATE.currentResults = JSON.parse(JSON.stringify(DEMO_DATA));
        STATE.versionHistory = [{
            version: 1,
            score: DEMO_DATA.original_score,
            timestamp: new Date().toLocaleString('ru-RU'),
            changes: [],
            resultsSnapshot: JSON.parse(JSON.stringify(DEMO_DATA))
        }];
        STATE.currentVersion = 1;

        displayResults(DEMO_DATA);
        updateLanguageBadge(DEMO_DATA.language);
        showToast('Демо-режим: пример ТЗ с оценкой 58 баллов', 'info');
    });
}

function setupModalListeners() {
    infoBtn.addEventListener('click', () => criteriaModal.classList.remove('hidden'));
    closeCriteriaBtn.addEventListener('click', () => criteriaModal.classList.add('hidden'));
    criteriaModal.addEventListener('click', (e) => {
        if (e.target === criteriaModal) criteriaModal.classList.add('hidden');
    });
}

// ============================================
// SERVER HEALTH
// ============================================
async function checkServerHealth() {
    try {
        const response = await fetch('/api/health');
        if (!response.ok) throw new Error();
        statusDot.classList.remove('offline');
        statusDot.title = 'Сервер доступен';
    } catch {
        statusDot.classList.add('offline');
        statusDot.title = 'Сервер недоступен';
        showServerBanner();
    }
}

function showServerBanner() {
    const banner = document.createElement('div');
    banner.className = 'server-error-banner';
    banner.textContent = '⚠️ Сервер недоступен. Убедитесь что backend запущен.';
    document.body.insertBefore(banner, document.body.firstChild);
    document.querySelector('.main-content').style.paddingTop = '46px';
}

// ============================================
// UTILS
// ============================================
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

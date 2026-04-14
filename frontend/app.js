// Application State
const STATE = {
    currentFileId: null,
    currentResults: null,
    versionHistory: [],
    currentVersion: 0
};

// Demo Data for testing
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
            original_text: "Государственная программа развития информационно-коммуникационных технологий\nНациональный стратегический план развития",
            suggested_fix: "Государственная программа развития информационно-коммуникационных технологий на 2022-2026 годы, п. 2.3 «Развитие научных исследований»\nНациональный стратегический план развития Республики Казахстан на 2025-2029 годы, раздел IV, п. 18"
        },
        {
            section: "Раздел 4.1: Прямые результаты",
            severity: "high",
            description: "Количество публикаций не указано, отсутствует информация о квартилях WoS/Scopus",
            original_text: "Будут опубликованы научные статьи в рецензируемых журналах",
            suggested_fix: "Минимум 3 статьи в журналах WoS с квартилем Q2 или выше, минимум 2 статьи в журналах Scopus первого квартиля"
        },
        {
            section: "Раздел 5: Финансирование",
            severity: "medium",
            description: "Указана общая сумма, но отсутствует разбивка по годам выполнения программы",
            original_text: "Общая сумма: 5,000,000 тенге",
            suggested_fix: "Общая сумма: 5,000,000 тенге\n2024 год: 1,500,000 тенге\n2025 год: 1,800,000 тенге\n2026 год: 1,700,000 тенге"
        },
        {
            section: "Раздел 2.2: Задачи",
            severity: "low",
            description: "Задачи сформулированы слишком общо, без конкретных измеримых показателей",
            original_text: "Провести исследования\nРазработать технологии",
            suggested_fix: "Провести экспериментальные исследования по оптимизации алгоритмов машинного обучения и подготовить 2 научных публикации\nРазработать прототип системы обработки данных в реальном времени с производительностью не менее 10,000 операций в секунду"
        }
    ],
    suggestions: [
        "Добавьте конкретные номера пунктов для каждого упоминаемого стратегического документа в Раздел 3",
        "Уточните количество требуемых публикаций с указанием баз индексирования и квартилей",
        "Разбейте общий бюджет по годам программы в Раздел 5",
        "Переформулируйте задачи с использованием SMART-критериев (специфичность, измеримость, достижимость)",
        "Добавьте в Раздел 4.2 подробное описание экономического, экологического и социального эффектов",
        "Указите конкретные целевые потребители результатов программы"
    ],
    corrected_sections: {},
    summary: "Техническое задание охватывает основные требуемые разделы, однако имеет значительные пробелы в конкретизации требований. Наиболее критичные проблемы: отсутствие ссылок на конкретные пункты стратегических документов, неопределённые показатели результатов и отсутствие разбивки бюджета по годам. После устранения выявленных проблем оценка может быть повышена до 85-90 баллов.",
    structure_check: {
        has_section_1: true,
        has_section_2: true,
        has_section_3: true,
        has_section_4_1: true,
        has_section_4_2: true,
        has_section_5: true
    }
};

// DOM Elements
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const uploadPage = document.getElementById('uploadPage');
const resultsPage = document.getElementById('resultsPage');
const historyPage = document.getElementById('historyPage');
const loadingOverlay = document.getElementById('loadingOverlay');
const toastContainer = document.getElementById('toastContainer');
const navLinks = document.querySelectorAll('.nav-link');
const applyFixesBtn = document.getElementById('applyFixesBtn');
const resetBtn = document.getElementById('resetBtn');
const downloadCorrectedBtn = document.getElementById('downloadCorrectedBtn');
const exportExcelBtn = document.getElementById('exportExcelBtn');
const exportAllBtn = document.getElementById('exportAllBtn');
const pageTitle = document.getElementById('pageTitle');
const infoBtn = document.getElementById('infoBtn');
const criteriaModal = document.getElementById('criteriaModal');
const closeCriteriaBtn = document.getElementById('closeCriteriaBtn');
const scoreComparison = document.getElementById('scoreComparison');
const demoBtn = document.getElementById('demoBtn');

// Initialize
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
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    uploadZone.addEventListener('click', () => {
        fileInput.click();
    });

    browseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
}

// ============================================
// FILE UPLOAD AND VALIDATION
// ============================================
function handleFileUpload(file) {
    const validExtensions = ['docx', 'pdf'];
    const fileExtension = file.name.split('.').pop().toLowerCase();
    const maxSize = 10 * 1024 * 1024;

    if (!validExtensions.includes(fileExtension)) {
        showToast('Поддерживаются только форматы .docx и .pdf', 'error');
        return;
    }

    if (file.size > maxSize) {
        showToast('Размер файла не должен превышать 10MB', 'error');
        return;
    }

    analyzeFile(file);
}

// ============================================
// API CALLS
// ============================================
async function analyzeFile(file) {
    showLoading();

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка при анализе документа');
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
    const checkboxes = document.querySelectorAll('.issue-checkbox:checked');
    const issuesToFix = Array.from(checkboxes).map(cb => {
        const card = cb.closest('.issue-card');
        return Array.from(document.querySelectorAll('.issue-card')).indexOf(card);
    });

    if (issuesToFix.length === 0) {
        showToast('Пожалуйста, выберите хотя бы одну проблему для исправления', 'warning');
        return;
    }

    showLoading();

    try {
        const response = await fetch('/api/apply-fix', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_id: STATE.currentFileId,
                issues_to_fix: issuesToFix,
                custom_instruction: ''
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка при применении исправлений');
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
        downloadCorrectedBtn.onclick = async () => {
            try {
                const response = await fetch(data.download_url);
                if (!response.ok) {
                    throw new Error('Ошибка при скачивании файла');
                }
                const blob = await response.blob();
                const filename = data.download_url.split('/').pop() || 'corrected_document.docx';
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                showToast('Файл успешно скачан', 'success');
            } catch (error) {
                showToast(`Ошибка при скачивании: ${error.message}`, 'error');
            }
        };

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

async function downloadExcel() {
    try {
        const response = await fetch('/api/download-excel');
        if (!response.ok) {
            throw new Error('Ошибка при скачивании файла');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'tz_scores.xlsx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showToast('Excel файл скачан успешно', 'success');
    } catch (error) {
        showToast(`Ошибка: ${error.message}`, 'error');
    }
}

async function loadHistory() {
    try {
        const response = await fetch('/api/records');
        if (!response.ok) {
            throw new Error('Ошибка при загрузке истории');
        }

        const data = await response.json();
        renderHistoryTable(data.records);
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// ============================================
// UI RENDERING
// ============================================
function displayResults(data) {
    document.getElementById('resultFilename').textContent = data.filename;

    const languageMap = {
        russian: 'РУС',
        kazakh: 'КАЗ'
    };
    const languageText = {
        russian: 'Русский язык',
        kazakh: 'Казахский язык'
    };

    const langBadge = languageMap[data.language] || 'РУС';
    const langText = languageText[data.language] || 'Русский язык';

    document.getElementById('resultLanguageBadge').textContent = langBadge;
    document.getElementById('resultLanguageText').textContent = langText;

    downloadCorrectedBtn.disabled = true;
    downloadCorrectedBtn.onclick = null;
    scoreComparison.classList.add('hidden');

    animateScoreGauge(data.original_score);
    renderScoreBreakdown(data.score_breakdown);
    renderIssues(data.issues);
    renderSuggestions(data.suggestions);
    document.getElementById('summaryText').textContent = data.summary;
    renderVersionHistory();

    showPage('results');
}

function animateScoreGauge(score) {
    const gaugeForeground = document.getElementById('gaugeForeground');
    const scoreNumber = document.getElementById('scoreNumber');

    const circumference = 2 * Math.PI * 80;
    const offset = circumference - (score / 100) * circumference;

    scoreNumber.textContent = '0';
    gaugeForeground.style.strokeDasharray = `0 ${circumference}`;

    if (score < 50) {
        gaugeForeground.className = 'gauge-foreground score-low';
    } else if (score < 75) {
        gaugeForeground.className = 'gauge-foreground score-medium';
    } else {
        gaugeForeground.className = 'gauge-foreground score-high';
    }

    const startTime = performance.now();
    const duration = 1000;

    function animate(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const currentScore = Math.round(progress * score);

        scoreNumber.textContent = currentScore;
        gaugeForeground.style.strokeDasharray = `${progress * circumference} ${circumference}`;

        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    }

    requestAnimationFrame(animate);
}

function renderScoreBreakdown(breakdown) {
    const container = document.getElementById('breakdownBars');
    container.innerHTML = '';

    const categories = [
        { key: 'section_completeness', label: 'Полнота разделов', max: 25 },
        { key: 'strategic_references', label: 'Ссылки на документы', max: 20 },
        { key: 'quantitative_results', label: 'Количественные результаты', max: 20 },
        { key: 'budget_breakdown', label: 'Разбор бюджета', max: 15 },
        { key: 'logical_consistency', label: 'Логическая согласованность', max: 10 },
        { key: 'language_clarity', label: 'Ясность языка', max: 10 }
    ];

    categories.forEach(cat => {
        const score = breakdown[cat.key] || 0;
        const percentage = (score / cat.max) * 100;

        const barHtml = `
            <div class="breakdown-bar">
                <div class="breakdown-label">
                    <span>${cat.label}</span>
                    <span>${score}/${cat.max}</span>
                </div>
                <div class="breakdown-progress">
                    <div class="breakdown-progress-bar" style="width: ${percentage}%"></div>
                </div>
            </div>
        `;
        container.innerHTML += barHtml;
    });

    document.querySelectorAll('.breakdown-progress-bar').forEach((bar, index) => {
        setTimeout(() => {
            const width = bar.style.width;
            bar.style.width = '0';
            setTimeout(() => {
                bar.style.width = width;
            }, 50);
        }, index * 100);
    });
}

function renderIssues(issues) {
    const container = document.getElementById('issuesList');
    container.innerHTML = '';

    if (issues.length === 0) {
        container.innerHTML = '<p style="color: var(--color-success); font-weight: 600;">Проблемы не обнаружены!</p>';
        return;
    }

    issues.forEach((issue, index) => {
        const severityClass = `severity-${issue.severity}`;
        const severityLabel = {
            high: 'ВЫСОКАЯ',
            medium: 'СРЕДНЯЯ',
            low: 'НИЗКАЯ'
        }[issue.severity] || 'НИЗКАЯ';

        const issueHtml = `
            <div class="issue-card ${severityClass}">
                <div class="issue-header">
                    <div class="issue-title">
                        <input type="checkbox" class="issue-checkbox" data-issue-index="${index}">
                        <span class="issue-section">${issue.section}</span>
                        <span class="severity-badge ${issue.severity}">${severityLabel}</span>
                    </div>
                </div>
                <div class="issue-description">${issue.description}</div>
                <div class="issue-details">
                    <div class="issue-text-block">
                        <div class="issue-label">Проблемный текст</div>
                        <div class="code-block">${escapeHtml(issue.original_text)}</div>
                    </div>
                    <div class="issue-text-block">
                        <div class="issue-label">Предложенное исправление</div>
                        <div class="highlight-block">${escapeHtml(issue.suggested_fix)}</div>
                    </div>
                </div>
            </div>
        `;
        container.innerHTML += issueHtml;
    });

    document.querySelectorAll('.issue-card').forEach(card => {
        card.addEventListener('click', function(e) {
            if (e.target.classList.contains('issue-checkbox')) {
                return;
            }
            const details = this.querySelector('.issue-details');
            details.classList.toggle('expanded');
        });
    });
}

function renderSuggestions(suggestions) {
    const container = document.getElementById('suggestionsList');
    container.innerHTML = '';

    suggestions.forEach(suggestion => {
        const li = document.createElement('li');
        li.textContent = suggestion;
        container.appendChild(li);
    });
}

function renderHistoryTable(records) {
    const tbody = document.getElementById('recordsTableBody');
    tbody.innerHTML = '';

    records.forEach(record => {
        const originalScore = record.original_score;
        const correctedScore = record.corrected_score;
        const improvement = correctedScore ? correctedScore - originalScore : null;

        let scoreClass = 'score-cell-high';
        if (originalScore < 50) {
            scoreClass = 'score-cell-low';
        } else if (originalScore < 75) {
            scoreClass = 'score-cell-medium';
        }

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${escapeHtml(record.filename)}</td>
            <td>${record.language === 'russian' ? 'Русский' : 'Казахский'}</td>
            <td><span class="${scoreClass}">${originalScore}</span></td>
            <td>${correctedScore !== null ? correctedScore : '-'}</td>
            <td>${improvement !== null ? (improvement > 0 ? '+' : '') + improvement : '-'}</td>
            <td>${record.timestamp}</td>
        `;
        tbody.appendChild(row);
    });
}

// ============================================
// UI HELPERS
// ============================================
function showPage(pageName) {
    document.querySelectorAll('[data-page]').forEach(el => {
        el.classList.remove('active');
    });

    uploadPage.classList.add('hidden');
    resultsPage.classList.add('hidden');
    historyPage.classList.add('hidden');

    navLinks.forEach(link => link.classList.remove('active'));

    if (pageName === 'upload') {
        uploadPage.classList.remove('hidden');
        pageTitle.textContent = 'Анализ ТЗ';
        document.querySelector('[data-page="upload"]').classList.add('active');
    } else if (pageName === 'results') {
        resultsPage.classList.remove('hidden');
        pageTitle.textContent = 'Результаты анализа';
    } else if (pageName === 'history') {
        historyPage.classList.remove('hidden');
        pageTitle.textContent = 'История оценок';
        document.querySelector('[data-page="history"]').classList.add('active');
        loadHistory();
    }
}

function showLoading() {
    loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 4000);
}

function setupNavigation() {
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            showPage(page);
        });
    });
}

function setupEventListeners() {
    applyFixesBtn.addEventListener('click', applySelectedFixes);
    resetBtn.addEventListener('click', () => {
        document.querySelectorAll('.issue-checkbox').forEach(cb => cb.checked = false);
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
    if (demoBtn) {
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
}

function setupModalListeners() {
    infoBtn.addEventListener('click', () => {
        criteriaModal.classList.remove('hidden');
    });

    closeCriteriaBtn.addEventListener('click', () => {
        criteriaModal.classList.add('hidden');
    });

    criteriaModal.addEventListener('click', (e) => {
        if (e.target === criteriaModal) {
            criteriaModal.classList.add('hidden');
        }
    });
}

// ============================================
// SERVER HEALTH CHECK
// ============================================
async function checkServerHealth() {
    try {
        const response = await fetch('/api/health', { method: 'GET' });
        if (!response.ok) {
            showServerErrorBanner();
        }
    } catch (error) {
        showServerErrorBanner();
    }
}

function showServerErrorBanner() {
    const banner = document.createElement('div');
    banner.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background-color: #ff4757;
        color: white;
        padding: 12px 16px;
        text-align: center;
        font-weight: 600;
        z-index: 1000;
        font-family: Inter, sans-serif;
    `;
    banner.textContent = '⚠️ Сервер недоступен. Проверьте что backend запущен.';
    document.body.insertBefore(banner, document.body.firstChild);

    // Add margin to main content
    document.querySelector('.main-content').style.marginTop = '46px';
}

// ============================================
// VERSION HISTORY AND SCORE COMPARISON
// ============================================
function updateLanguageBadge(language) {
    const langData = {
        russian: { badge: '🇷🇺 Русский', color: 'blue' },
        kazakh: { badge: '🇰🇿 Қазақша', color: 'gold' }
    };

    const data = langData[language] || langData['russian'];
    const badge = document.getElementById('languageBadge');
    badge.textContent = data.badge;
    if (data.color === 'gold') {
        badge.style.backgroundColor = '#d4a574';
    }
}

function showScoreComparison(oldScore, newScore) {
    document.getElementById('comparisonBefore').textContent = oldScore;
    document.getElementById('comparisonAfter').textContent = newScore;
    const improvement = newScore - oldScore;
    document.getElementById('comparisonImprovement').textContent = (improvement > 0 ? '+' : '') + improvement;
    scoreComparison.classList.remove('hidden');
}

function animateScoreGaugeFromTo(fromScore, toScore) {
    const gaugeForeground = document.getElementById('gaugeForeground');
    const scoreNumber = document.getElementById('scoreNumber');

    const circumference = 2 * Math.PI * 80;
    const startOffset = circumference - (fromScore / 100) * circumference;
    const endOffset = circumference - (toScore / 100) * circumference;

    scoreNumber.textContent = fromScore;
    gaugeForeground.style.strokeDasharray = `${(fromScore / 100) * circumference} ${circumference}`;

    if (toScore < 50) {
        gaugeForeground.className = 'gauge-foreground score-low';
    } else if (toScore < 75) {
        gaugeForeground.className = 'gauge-foreground score-medium';
    } else {
        gaugeForeground.className = 'gauge-foreground score-high';
    }

    const startTime = performance.now();
    const duration = 1000;

    function animate(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const currentScore = Math.round(fromScore + progress * (toScore - fromScore));

        scoreNumber.textContent = currentScore;
        const currentDashOffset = (currentScore / 100) * circumference;
        gaugeForeground.style.strokeDasharray = `${currentDashOffset} ${circumference}`;

        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    }

    requestAnimationFrame(animate);
}

function renderVersionHistory() {
    const container = document.getElementById('versionHistory');

    if (STATE.versionHistory.length === 0) {
        container.innerHTML = '';
        return;
    }

    let html = '<h3>История версий</h3><div class="version-timeline">';

    STATE.versionHistory.forEach((version, index) => {
        const isLatest = index === STATE.versionHistory.length - 1;
        const changesHtml = version.changes.length > 0
            ? `<div class="version-changes"><ul>${version.changes.map(c => `<li>${escapeHtml(c)}</li>`).join('')}</ul></div>`
            : '';

        const improvementBadge = index > 0 && version.score > STATE.versionHistory[index - 1].score
            ? `<div class="version-improvement-badge">улучшение: +${version.score - STATE.versionHistory[index - 1].score}</div>`
            : '';

        const restoreBtn = !isLatest
            ? `<button class="btn btn-secondary" onclick="restoreVersion(${index})">Вернуться к версии ${version.version}</button>`
            : '';

        html += `
            <div class="version-item">
                <div class="version-number">Версия ${version.version}</div>
                <div class="version-score">Оценка: ${version.score}/100</div>
                <div class="version-timestamp">${version.timestamp}</div>
                ${improvementBadge}
                ${changesHtml}
                ${restoreBtn}
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}

function restoreVersion(versionIndex) {
    const version = STATE.versionHistory[versionIndex];
    STATE.currentResults = JSON.parse(JSON.stringify(version.resultsSnapshot));
    STATE.currentVersion = version.version;

    animateScoreGauge(version.score);
    renderScoreBreakdown(version.resultsSnapshot.score_breakdown);
    renderIssues(version.resultsSnapshot.issues);
    renderSuggestions(version.resultsSnapshot.suggestions);
    document.getElementById('summaryText').textContent = version.resultsSnapshot.summary;

    scoreComparison.classList.add('hidden');
    showToast(`Восстановлена версия ${version.version}`, 'info');
}

// ============================================
// UTILITIES
// ============================================
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

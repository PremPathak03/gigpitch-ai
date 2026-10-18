/**
 * GigPitch AI — Frontend Application Logic
 */

// ─── Preset Templates ───
const PRESETS = {
    react: {
        job: `Looking for a Senior React/Next.js developer to rebuild our B2B SaaS dashboard. 
Requirements:
- Convert complex Figma designs into responsive Tailwind components
- Connect to 5+ REST API endpoints with real-time data refreshes
- Sub-second page load performance and clean state management
- Budget: $1,200 - $1,800. Timeline: 10-14 days.`,
        skills: `Full-Stack React & Next.js specialist with 4+ years of experience. Expert in Tailwind CSS, TanStack Query, TypeScript, and high-performance charts. Built 12+ production dashboards with 5-star ratings.`
    },
    mobile: {
        job: `We need a skilled Flutter or React Native developer to finish our MVP mobile app for personal trainers and clients.
Core tasks:
- Workout scheduling calendar with push notifications
- Stripe in-app subscriptions integration
- Offline-first caching with SQLite/Hive
- Must be ready for App Store & Google Play submission in 3 weeks.`,
        skills: `Cross-platform mobile developer with 3+ published React Native and Flutter apps. Deep expertise in Stripe payments, push notifications, and offline data sync architectures.`
    },
    python: {
        job: `Seeking a Python engineer to build an automated real estate market scraper.
Deliverables:
- Scrape 4 regional MLS listings daily without getting rate-limited or CAPTCHA blocked
- Normalize and deduplicate property data into PostgreSQL
- Send daily summary alerts via Telegram/Discord webhook
- Must include logging, Docker containerization, and clean documentation.`,
        skills: `Python automation specialist. Expert in Playwright, BeautifulSoup, async httpx, PostgreSQL, and Docker. Have engineered resilient crawlers processing 100k+ records/day with rotating proxies.`
    }
};

// ─── DOM References ───
const form = document.getElementById('pitch-form');
const jobDescInput = document.getElementById('job-desc');
const skillsInput = document.getElementById('skills');
const jobCharCount = document.getElementById('job-char-count');
const skillsCharCount = document.getElementById('skills-char-count');
const generateBtn = document.getElementById('generate-btn');
const btnIcon = document.getElementById('btn-icon');
const btnText = document.getElementById('btn-text');
const clearFormBtn = document.getElementById('clear-form-btn');

const outputEmpty = document.getElementById('output-empty');
const outputLoading = document.getElementById('output-loading');
const outputContent = document.getElementById('output-content');
const outputError = document.getElementById('output-error');
const errorMessageEl = document.getElementById('error-message');
const retryBtn = document.getElementById('retry-btn');
const proposalBox = document.getElementById('proposal-box');
const wordCountEl = document.getElementById('word-count');
const readTimeEl = document.getElementById('read-time');

const copyBtn = document.getElementById('copy-btn');
const copyIcon = document.getElementById('copy-icon');
const copyText = document.getElementById('copy-text');
const saveBtn = document.getElementById('save-btn');
const regenBtn = document.getElementById('regen-btn');

const historyToggle = document.getElementById('history-toggle');
const historyDrawer = document.getElementById('history-drawer');
const historyCloseBtn = document.getElementById('history-close-btn');
const drawerBackdrop = document.getElementById('drawer-backdrop');
const historyContainer = document.getElementById('history-items-container');
const historyCounter = document.getElementById('history-counter');
const clearAllHistoryBtn = document.getElementById('clear-all-history');

const toastEl = document.getElementById('toast');
const toastIcon = document.getElementById('toast-icon');
const toastText = document.getElementById('toast-text');
const modelIndicator = document.getElementById('model-indicator');

// ─── State ───
let currentProposal = '';
let isGenerating = false;
let abortController = null;

// ─── Initialization ───
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    renderHistory();
    updateCharCounters();
    bindEvents();
});

// ─── Event Bindings ───
function bindEvents() {
    form.addEventListener('submit', handleFormSubmit);
    regenBtn.addEventListener('click', handleFormSubmit);
    retryBtn.addEventListener('click', handleFormSubmit);

    jobDescInput.addEventListener('input', updateCharCounters);
    skillsInput.addEventListener('input', updateCharCounters);

    clearFormBtn.addEventListener('click', () => {
        jobDescInput.value = '';
        skillsInput.value = '';
        updateCharCounters();
        jobDescInput.focus();
        showToast('Form cleared', '🧹');
    });

    // Preset buttons
    document.querySelectorAll('.preset-chip').forEach(btn => {
        btn.addEventListener('click', () => {
            const presetKey = btn.dataset.preset;
            if (PRESETS[presetKey]) {
                jobDescInput.value = PRESETS[presetKey].job;
                skillsInput.value = PRESETS[presetKey].skills;
                updateCharCounters();
                showToast(`Loaded ${presetKey.toUpperCase()} preset`, '✨');
            }
        });
    });

    copyBtn.addEventListener('click', copyProposal);
    saveBtn.addEventListener('click', saveProposal);

    // History drawer controls
    historyToggle.addEventListener('click', openHistoryDrawer);
    historyCloseBtn.addEventListener('click', closeHistoryDrawer);
    drawerBackdrop.addEventListener('click', closeHistoryDrawer);
    clearAllHistoryBtn.addEventListener('click', clearAllHistory);
}

// ─── Backend Health Check ───
async function checkHealth() {
    try {
        const res = await fetch('/api/health');
        if (res.ok) {
            const data = await res.json();
            if (data.model) {
                modelIndicator.textContent = `${data.model} (Active)`;
            }
        }
    } catch (e) {
        modelIndicator.textContent = 'Backend Offline';
        modelIndicator.previousElementSibling.classList.remove('bg-hf-emerald');
        modelIndicator.previousElementSibling.classList.add('bg-red-500');
    }
}

// ─── Character & Word Counters ───
function updateCharCounters() {
    jobCharCount.textContent = `${jobDescInput.value.length} chars`;
    skillsCharCount.textContent = `${skillsInput.value.length} chars`;
}

function updateWordAndReadStats(text) {
    const words = text.trim() ? text.trim().split(/\s+/).filter(Boolean).length : 0;
    wordCountEl.textContent = `${words} words`;
    wordCountEl.classList.remove('hidden');

    const readMinutes = Math.max(1, Math.round(words / 150));
    readTimeEl.textContent = `· ~${readMinutes} min read`;
    readTimeEl.classList.remove('hidden');
}

// ─── Form Submission & Streaming ───
async function handleFormSubmit(e) {
    if (e) e.preventDefault();
    if (isGenerating) return;

    const job_description = jobDescInput.value.trim();
    const skills = skillsInput.value.trim();
    const tone = document.querySelector('input[name="tone"]:checked')?.value || 'professional';

    if (!job_description) {
        showToast('Please paste a job description', '⚠️');
        jobDescInput.focus();
        return;
    }
    if (!skills) {
        showToast('Please enter your skills', '⚠️');
        skillsInput.focus();
        return;
    }

    // Prepare UI for generation
    setLoadingState(true);
    currentProposal = '';
    proposalBox.textContent = '';
    proposalBox.classList.add('streaming-cursor');

    outputEmpty.classList.add('hidden');
    outputError.classList.add('hidden');
    outputLoading.classList.remove('hidden');
    outputContent.classList.add('hidden');

    abortController = new AbortController();

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ job_description, skills, tone }),
            signal: abortController.signal,
        });

        if (!response.ok) {
            const errJson = await response.json().catch(() => ({}));
            throw new Error(errJson.error || `Server returned error (${response.status})`);
        }

        outputLoading.classList.add('hidden');
        outputContent.classList.remove('hidden');

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                const trimmed = line.trim();
                if (!trimmed.startsWith('data:')) continue;

                const payloadStr = trimmed.replace(/^data:\s*/, '');
                if (!payloadStr) continue;

                try {
                    const parsed = JSON.parse(payloadStr);
                    if (parsed.error) {
                        throw new Error(parsed.error);
                    }
                    if (parsed.text) {
                        currentProposal += parsed.text;
                        proposalBox.textContent = currentProposal;
                        updateWordAndReadStats(currentProposal);
                        proposalBox.scrollTop = proposalBox.scrollHeight;
                    }
                    if (parsed.done) {
                        break;
                    }
                } catch (parseErr) {
                    if (parseErr.message && !parseErr.message.includes('JSON')) {
                        throw parseErr;
                    }
                }
            }
        }

        proposalBox.classList.remove('streaming-cursor');
        showToast('Proposal crafted!', '🚀');

    } catch (err) {
        if (err.name === 'AbortError') return;
        console.error('Generation error:', err);
        outputLoading.classList.add('hidden');
        outputContent.classList.add('hidden');
        outputError.classList.remove('hidden');
        errorMessageEl.textContent = err.message || 'Failed to generate proposal. Please try again.';
    } finally {
        setLoadingState(false);
    }
}

function setLoadingState(loading) {
    isGenerating = loading;
    generateBtn.disabled = loading;
    if (loading) {
        btnIcon.textContent = '⏳';
        btnText.textContent = 'Drafting proposal...';
    } else {
        btnIcon.textContent = '⚡';
        btnText.textContent = 'Generate Winning Proposal';
        proposalBox.classList.remove('streaming-cursor');
    }
}

// ─── Clipboard Copy ───
async function copyProposal() {
    if (!currentProposal) return;

    try {
        await navigator.clipboard.writeText(currentProposal);
        copyIcon.textContent = '✅';
        copyText.textContent = 'Copied!';
        showToast('Copied proposal to clipboard!', '📋');
        setTimeout(() => {
            copyIcon.textContent = '📋';
            copyText.textContent = 'Copy Proposal';
        }, 2000);
    } catch {
        const tempArea = document.createElement('textarea');
        tempArea.value = currentProposal;
        document.body.appendChild(tempArea);
        tempArea.select();
        document.execCommand('copy');
        document.body.removeChild(tempArea);
        showToast('Copied to clipboard!', '📋');
    }
}

// ─── LocalStorage History ───
const STORAGE_KEY = 'gigpitch_saved_proposals';

function getSavedProposals() {
    try {
        return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    } catch {
        return [];
    }
}

function saveProposal() {
    if (!currentProposal) return;

    const list = getSavedProposals();
    const jobSnippet = jobDescInput.value.trim().substring(0, 90) + '...';
    const tone = document.querySelector('input[name="tone"]:checked')?.value || 'professional';

    const item = {
        id: 'gp_' + Date.now(),
        timestamp: new Date().toLocaleString(),
        snippet: jobSnippet,
        job: jobDescInput.value.trim(),
        skills: skillsInput.value.trim(),
        tone: tone,
        proposal: currentProposal,
    };

    list.unshift(item);
    if (list.length > 25) list.pop(); // keep top 25

    localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
    renderHistory();
    showToast('Proposal saved to history!', '⭐');
}

function renderHistory() {
    const list = getSavedProposals();
    historyCounter.textContent = list.length;

    if (list.length === 0) {
        historyContainer.innerHTML = `
            <div class="text-center py-12 text-slate-500">
                <span class="text-3xl">📭</span>
                <p class="text-xs font-medium mt-2">No saved proposals</p>
                <p class="text-[11px] text-slate-600 mt-0.5">Click ⭐ Save to store a proposal.</p>
            </div>
        `;
        return;
    }

    historyContainer.innerHTML = list.map(item => `
        <div class="history-card" data-id="${item.id}">
            <div class="flex items-center justify-between text-[11px] text-slate-400 mb-1">
                <span class="font-mono">${item.timestamp}</span>
                <span class="px-1.5 py-0.5 rounded bg-white/5 border border-white/10 text-hf-gold text-[10px] capitalize">${item.tone}</span>
            </div>
            <p class="text-xs text-slate-200 line-clamp-2 font-mono mb-2">${escapeHtml(item.snippet)}</p>
            <div class="flex items-center justify-between pt-1 border-t border-white/5">
                <button type="button" class="load-history-btn text-[11px] text-hf-gold hover:underline font-medium" data-id="${item.id}">
                    Load into view
                </button>
                <button type="button" class="delete-history-btn text-[11px] text-red-400 hover:text-red-300" data-id="${item.id}">
                    Delete
                </button>
            </div>
        </div>
    `).join('');

    // Attach listeners to dynamically created cards
    historyContainer.querySelectorAll('.load-history-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = btn.dataset.id;
            loadHistoryItem(id);
        });
    });

    historyContainer.querySelectorAll('.delete-history-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = btn.dataset.id;
            deleteHistoryItem(id);
        });
    });
}

function loadHistoryItem(id) {
    const list = getSavedProposals();
    const item = list.find(x => x.id === id);
    if (!item) return;

    jobDescInput.value = item.job || '';
    skillsInput.value = item.skills || '';
    updateCharCounters();

    const toneRadio = document.querySelector(`input[name="tone"][value="${item.tone}"]`);
    if (toneRadio) toneRadio.checked = true;

    currentProposal = item.proposal;
    proposalBox.textContent = currentProposal;
    updateWordAndReadStats(currentProposal);

    outputEmpty.classList.add('hidden');
    outputError.classList.add('hidden');
    outputLoading.classList.add('hidden');
    outputContent.classList.remove('hidden');

    closeHistoryDrawer();
    showToast('Loaded saved proposal', '📄');
}

function deleteHistoryItem(id) {
    let list = getSavedProposals();
    list = list.filter(x => x.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
    renderHistory();
    showToast('Item deleted', '🗑️');
}

function clearAllHistory() {
    if (!confirm('Clear all saved proposals?')) return;
    localStorage.removeItem(STORAGE_KEY);
    renderHistory();
    showToast('History cleared', '🧹');
}

// ─── History Drawer UI ───
function openHistoryDrawer() {
    historyDrawer.classList.remove('translate-x-full');
    drawerBackdrop.classList.remove('hidden');
}

function closeHistoryDrawer() {
    historyDrawer.classList.add('translate-x-full');
    drawerBackdrop.classList.add('hidden');
}

// ─── Toast System ───
let toastTimer = null;
function showToast(text, icon = '✨') {
    toastIcon.textContent = icon;
    toastText.textContent = text;
    toastEl.classList.add('toast-active');

    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
        toastEl.classList.remove('toast-active');
    }, 2800);
}

function escapeHtml(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

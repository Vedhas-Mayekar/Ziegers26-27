/* ============================================================
   ZIEGERS 2026-27 | DeCipher — Interactive Controls
   ============================================================ */

// Initialize Lucide Icons
document.addEventListener('DOMContentLoaded', function () {
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});

// ---------------------------------------------------------------------------
// Registration Countdown Timer (live — closes at midnight Aug 29, 2026)
// ---------------------------------------------------------------------------
function startCountdown() {
    const countdownEl = document.getElementById('countdown');
    if (!countdownEl) return;

    // Deadline: 29th August 2026 at 00:00 (midnight) IST
    const deadline = new Date('2026-08-29T00:00:00+05:30').getTime();

    let timerId = null;

    function pad(n) {
        return String(n).padStart(2, '0');
    }

    function updateTimer() {
        const now = Date.now();
        const diff = deadline - now;

        if (diff <= 0) {
            countdownEl.textContent = '00 Days : 00 Hrs : 00 Mins : 00 Secs';
            if (timerId !== null) {
                clearInterval(timerId);
            }
            return;
        }

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const secs = Math.floor((diff % (1000 * 60)) / 1000);

        countdownEl.textContent = `${pad(days)} Days : ${pad(hours)} Hrs : ${pad(mins)} Mins : ${pad(secs)} Secs`;
    }

    updateTimer();
    timerId = setInterval(updateTimer, 1000);
}

// Start the countdown once the page is ready
startCountdown();

// ---------------------------------------------------------------------------
// Audio Effects Synthesizer (Web Audio API - No external audio required)
// ---------------------------------------------------------------------------
let soundEnabled = true;
let audioCtx = null;
let bgAudioStarted = false;

function getAudioCtx() {
    if (!audioCtx) {
        try {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
            audioCtx = null;
        }
    }
    return audioCtx;
}

// Start background investigation theme on first user interaction.
// Browsers block autoplay with sound, so we start it after the first click/tap/keypress.
function startBackgroundMusic() {
    if (bgAudioStarted || !soundEnabled) return;
    const bgAudio = document.getElementById('bg-audio');
    if (!bgAudio) return;
    bgAudio.volume = 0.25; // Set to 25% volume

    // play() returns a Promise that rejects on mobile when autoplay is blocked.
    // Using the two-argument .then(onFulfilled, onRejected) form registers the
    // rejection handler in the SAME call, so the promise is considered handled
    // immediately. This prevents Chrome DevTools (especially mobile emulation)
    // from pausing on the expected autoplay-block rejection
    // ("Paused on promise rejection").
    const playPromise = bgAudio.play();
    if (playPromise !== undefined && typeof playPromise.then === 'function') {
        playPromise.then(
            function () { bgAudioStarted = true; },
            function () { /* Autoplay blocked - will retry on next interaction. */ }
        );
    } else {
        // Non-Promise .play() (older browsers / autoplay already allowed)
        bgAudioStarted = true;
    }
}

// Attempt to start the theme audio once per genuine user interaction.
// Uses once:true so each listener auto-removes after firing. If the browser
// still blocked autoplay, re-bind so the next tap/click retries. This is the
// cleanest cross-browser way to honour the autoplay-policy on mobile and avoids
// the duplicate-listener + redundant call bugs of the previous implementation.
function tryStartBackgroundMusic() {
    startBackgroundMusic();
    // Ensure AudioContext is allowed to run once unlocked by a gesture
    const ctx = getAudioCtx();
    if (ctx && ctx.state === 'suspended') {
        ctx.resume();
    }
    if (!bgAudioStarted) {
        ['click', 'keydown', 'touchstart'].forEach(function (evt) {
            window.addEventListener(evt, tryStartBackgroundMusic, { once: true, passive: true });
        });
    }
}

['click', 'keydown', 'touchstart'].forEach(function (evt) {
    window.addEventListener(evt, tryStartBackgroundMusic, { once: true, passive: true });
});

function playClickSound() {
    if (!soundEnabled) return;
    const ctx = getAudioCtx();
    if (!ctx) return;
    try {
        if (ctx.state === 'suspended') {
            ctx.resume();
        }
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(400, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(120, ctx.currentTime + 0.04);
        gain.gain.setValueAtTime(0.15, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.04);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.04);
    } catch (e) { /* silently ignore audio errors */ }
}

function toggleAudio() {
    soundEnabled = !soundEnabled;

    // Toggle background investigation theme audio
    const bgAudio = document.getElementById('bg-audio');
    if (bgAudio) {
        if (soundEnabled) {
            // Try to play (may be blocked if there has been no user gesture yet)
            bgAudio.volume = 0.25; // Keep at 25% volume
            const playPromise = bgAudio.play();
            if (playPromise !== undefined && typeof playPromise.then === 'function') {
                playPromise.then(
                    function () { /* playback started */ },
                    function () {
                        // Autoplay blocked by browser - user needs a click to enable
                        bgAudio.pause();
                        bgAudio.currentTime = 0;
                    }
                );
            }
            document.getElementById('audio-icon').setAttribute('data-lucide', 'volume-2');
        } else {
            bgAudio.pause();
            bgAudio.currentTime = 0; // Reset to start
            document.getElementById('audio-icon').setAttribute('data-lucide', 'volume-x');
        }
    }

    // Toggle click sound effect icon
    const icon = document.getElementById('audio-icon');
    if (icon) {
        if (soundEnabled) {
            icon.setAttribute('data-lucide', 'volume-2');
        } else {
            icon.setAttribute('data-lucide', 'volume-x');
        }
    }
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

// ---------------------------------------------------------------------------
// Dark Mode / Torch (REVERSED: dark mode ON by default)
// Persisted globally in localStorage so the light stays on/off across pages.
// ---------------------------------------------------------------------------
const TORCH_STORAGE_KEY = 'ziegers_torch_active';

// Read the saved torch state (default: dark mode ON = torchActive true)
function getInitialTorchState() {
    try {
        const saved = localStorage.getItem(TORCH_STORAGE_KEY);
        if (saved !== null) {
            return saved === 'true';
        }
    } catch (e) { /* localStorage unavailable — fall back to default */ }
    return true; // Default = dark mode on
}

let torchActive = getInitialTorchState();
const torchOverlay = document.getElementById('torch-overlay');
const darkModeWarning = document.getElementById('dark-mode-warning');
const torchBtn = document.getElementById('torch-btn');
const torchIcon = torchBtn ? torchBtn.querySelector('i') : null;
const torchBtnText = torchBtn ? torchBtn.querySelector('span') : null;

function applyTorchState() {
    document.documentElement.classList.toggle('torch-dark', torchActive);
    if (torchOverlay) {
        torchOverlay.style.opacity = torchActive ? '1' : '0';
    }
    // Show warning banner while dark mode is active
    if (darkModeWarning) {
        darkModeWarning.style.display = torchActive ? 'block' : 'none';
    }
    // Torch icon: lit torch when lights are on, struck-through torch when dark mode (torch off)
    if (torchIcon) {
        torchIcon.setAttribute('data-lucide', 'flashlight');
        torchIcon.classList.toggle('line-through', torchActive);
    }
    if (torchBtnText) {
        torchBtnText.textContent = torchActive ? 'Dark' : 'Light';
    }
    if (torchBtn) {
        torchBtn.title = torchActive ? 'Turn on the lights to solve the case' : 'Turn off the lights (Dark Mode)';
    }
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

function toggleTorch() {
    playClickSound();
    torchActive = !torchActive; // Toggle between dark mode and lights-on
    // Persist the state so it stays consistent across all pages
    try {
        localStorage.setItem(TORCH_STORAGE_KEY, String(torchActive));
    } catch (e) { /* localStorage unavailable — state persists only for this session */ }
    applyTorchState();
}

// Preserve the state across immediate page navigation and sync it with other
// open ZIEGERS pages that share the same browser storage.
window.addEventListener('pagehide', () => {
    try { localStorage.setItem(TORCH_STORAGE_KEY, String(torchActive)); } catch (e) { /* ignore */ }
});
window.addEventListener('storage', (event) => {
    if (event.key === TORCH_STORAGE_KEY && event.newValue !== null) {
        torchActive = event.newValue === 'true';
        applyTorchState();
    }
});
window.addEventListener('pageshow', () => {
    // Covers browser back/forward cache restores, which do not re-run scripts.
    torchActive = getInitialTorchState();
    applyTorchState();
});

// Initialize dark mode on page load
applyTorchState();

window.addEventListener('mousemove', (e) => {
    if (torchActive) {
        torchOverlay.style.setProperty('--x', `${e.clientX}px`);
        torchOverlay.style.setProperty('--y', `${e.clientY}px`);
    }
});

// ---------------------------------------------------------------------------
// Mouse Glow Effect
// ---------------------------------------------------------------------------
let mouseGlowActive = true;
const mouseGlow = document.getElementById('mouse-glow');

function updateMouseGlow(e) {
    if (!mouseGlowActive) return;
    mouseGlow.style.setProperty('--glow-x', `${e.clientX}px`);
    mouseGlow.style.setProperty('--glow-y', `${e.clientY}px`);
}

window.addEventListener('mousemove', updateMouseGlow);

// ---------------------------------------------------------------------------
// Case Event Filter Logic
// ---------------------------------------------------------------------------
function filterCases(category) {
    playClickSound();
    const items = document.querySelectorAll('.case-item');
    const tabs = document.querySelectorAll('.filter-tab');

    tabs.forEach(tab => {
        tab.classList.remove('bg-stamp-red', 'text-white', 'font-bold');
        tab.classList.add('text-parchment-300');
    });

    const activeTab = document.getElementById(`tab-${category}`);
    if (activeTab) {
        activeTab.classList.add('bg-stamp-red', 'text-white', 'font-bold');
        activeTab.classList.remove('text-parchment-300');
    }

    items.forEach(item => {
        if (category === 'all') {
            item.classList.remove('hidden');
        } else {
            if (item.classList.contains(category)) {
                item.classList.remove('hidden');
            } else {
                item.classList.add('hidden');
            }
        }
    });
}

// ---------------------------------------------------------------------------
// Case details store - populated from Django's json_script serialization.
// ---------------------------------------------------------------------------
const caseDetailsData = getCaseData();

function getCaseData() {
    const script = document.getElementById('case-details-data');
    if (script) {
        try {
            return JSON.parse(script.textContent);
        } catch (e) {
            return {};
        }
    }
    return {};
}

// ---------------------------------------------------------------------------
// Modal Handlers
// ---------------------------------------------------------------------------
function openCaseModal(caseKey) {
    playClickSound();
    const data = caseDetailsData[caseKey];
    if (!data) return;

    const modalBody = document.getElementById('modal-body');
    if (!modalBody) return;

    modalBody.innerHTML = `
        <div class="space-y-4">
            <span class="stamp-mark px-2 py-0.5 text-xs font-bold uppercase typewriter-text">${data.case_no}</span>
            <h3 class="text-3xl font-black title-cinzel text-white">${data.title}</h3>
            <div class="text-sm font-bold text-stamp-gold typewriter-text">REGISTRATION FEE: ${data.fee}</div>

            <p class="text-xs sm:text-sm text-parchment-200 leading-relaxed border-t border-b border-noir-700 py-3">
                ${data.desc}
            </p>

            <div>
                <h4 class="text-xs font-bold text-stamp-red typewriter-text uppercase tracking-wider mb-2">RULES & INVESTIGATION DIRECTIVES:</h4>
                <ul class="space-y-2 text-xs text-parchment-300 typewriter-text list-disc pl-4">
                    ${data.rules.map(r => `<li>${r}</li>`).join('')}
                </ul>
            </div>

            <div class="pt-4 border-t border-noir-700 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div class="text-xs typewriter-text text-parchment-400">
                    <strong>Contact Officers:</strong><br>
                    ${data.officers.map(o => `${o.name} (<a href="tel:${o.phone}" class="text-stamp-gold hover:underline">${o.phone}</a>)`).join(' • ')}
                </div>
                ${caseKey === 'codesprint'
                    ? '<button onclick="closeCaseModal(); openCodeSprintRegistration();" class="w-full sm:w-auto px-6 py-2.5 bg-stamp-red hover:bg-red-700 text-white font-extrabold text-xs uppercase tracking-wider rounded border border-red-500">REGISTER NOW</button>'
                    : '<span class="text-xs typewriter-text text-parchment-400">Registration details available from the event officers.</span>'}
            </div>
        </div>
    `;

    document.getElementById('case-modal').classList.remove('hidden');
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

function closeCaseModal() {
    playClickSound();
    document.getElementById('case-modal').classList.add('hidden');
}

function openRegisterModal(title, price) {
    openCodeSprintRegistration();
}

function closeRegisterModal() {
    playClickSound();
    document.getElementById('register-modal').classList.add('hidden');
}

const GOOGLE_FORM_RESPONSE_URL = 'https://docs.google.com/forms/d/e/1FAIpQLSezCly9RvWmHngTWN-t1jrRZSojNixqyosRR6ArE0CftdojPw/formResponse';
const CLOUDINARY_UPLOAD_URL = 'https://api.cloudinary.com/v1_1/npptddim/image/upload';
const CLOUDINARY_UPLOAD_PRESET = 'ziegers_decipher_payment_receipts';
const RECEIPT_IMAGE_TYPES = new Set(['image/jpeg', 'image/png', 'image/webp']);
let receiptUploadToken = 0;
let nativeGoogleSubmissionPending = false;

function openGeneralRegistration() {
    openCodeSprintRegistration();
}

function getRegistrationForm() {
    return document.getElementById('codesprint-registration-form');
}

function setReceiptStatus(message, state) {
    const status = document.getElementById('receipt-upload-status');
    status.textContent = message;
    status.className = `receipt-status ${state ? `is-${state}` : ''}`;
    status.classList.toggle('hidden', !message);
}

function updateRegistrationSubmitState() {
    const form = getRegistrationForm();
    const submitButton = document.getElementById('registration-submit');
    const receiptUrl = document.getElementById('payment-receipt-url')?.value;
    const isUploading = document.getElementById('payment-receipt')?.dataset.uploading === 'true';
    if (!form || !submitButton || form.dataset.submitting === 'true') return;
    submitButton.disabled = !form.checkValidity() || !receiptUrl || isUploading;
}

function resetReceiptEvidence() {
    const receiptInput = document.getElementById('payment-receipt');
    const receiptUrl = document.getElementById('payment-receipt-url');
    const fileName = document.getElementById('receipt-file-name');
    receiptUploadToken += 1;
    if (receiptInput) {
        receiptInput.value = '';
        receiptInput.dataset.uploading = '';
    }
    if (receiptUrl) receiptUrl.value = '';
    if (fileName) {
        fileName.textContent = '';
        fileName.classList.add('hidden');
    }
    setReceiptStatus('', '');
    updateRegistrationSubmitState();
}

async function uploadPaymentReceipt(file) {
    const receiptInput = document.getElementById('payment-receipt');
    const receiptUrl = document.getElementById('payment-receipt-url');
    const fileName = document.getElementById('receipt-file-name');
    const uploadToken = ++receiptUploadToken;
    receiptUrl.value = '';
    receiptInput.dataset.uploading = 'true';
    fileName.textContent = `Selected evidence: ${file.name}`;
    fileName.classList.remove('hidden');
    setReceiptStatus('Uploading receipt evidence…', 'uploading');
    updateRegistrationSubmitState();

    const uploadData = new FormData();
    uploadData.append('file', file);
    uploadData.append('upload_preset', CLOUDINARY_UPLOAD_PRESET);

    try {
        const response = await fetch(CLOUDINARY_UPLOAD_URL, { method: 'POST', body: uploadData });
        const data = await response.json();
        if (!response.ok || !data.secure_url || !data.secure_url.startsWith('https://res.cloudinary.com/')) {
            throw new Error(data.error?.message || 'Cloudinary did not return a valid receipt URL.');
        }
        if (uploadToken !== receiptUploadToken) return;
        receiptUrl.value = data.secure_url;
        setReceiptStatus('Upload successful — receipt evidence secured.', 'success');
    } catch (error) {
        if (uploadToken !== receiptUploadToken) return;
        receiptUrl.value = '';
        setReceiptStatus('Receipt upload failed. Please select the image and try again.', 'error');
    } finally {
        if (uploadToken === receiptUploadToken) {
            receiptInput.dataset.uploading = '';
            updateRegistrationSubmitState();
        }
}
}

function openCodeSprintRegistration() {
    playClickSound();
    const form = document.getElementById('codesprint-registration-form');
    document.getElementById('registration-form-panel').classList.remove('hidden');
    document.getElementById('registration-success').classList.add('hidden');
    document.getElementById('registration-error').classList.add('hidden');
    if (form && !form.dataset.submitting) {
        form.reset();
        resetReceiptEvidence();
    }
    updateDuoFields();
    document.getElementById('register-modal').classList.remove('hidden');
    if (typeof lucide !== 'undefined') lucide.createIcons();
}

function updateDuoFields() {
    const isDuo = document.querySelector('input[name="entry.856098371"]:checked')?.value === 'Duo';
    const duoFields = document.getElementById('duo-fields');
    if (!duoFields) return;
    duoFields.classList.toggle('hidden', !isDuo);
    duoFields.querySelectorAll('.duo-required').forEach((input) => {
        input.required = isDuo;
        input.disabled = !isDuo;
        if (!isDuo) input.value = '';
    });
}

function showRegistrationError(message) {
    const error = document.getElementById('registration-error');
    error.textContent = message;
    error.classList.remove('hidden');
}

document.addEventListener('change', (event) => {
    if (event.target.matches('input[name="entry.856098371"]')) updateDuoFields();
    if (event.target.id === 'payment-receipt') {
        const file = event.target.files?.[0];
        if (!file) {
            resetReceiptEvidence();
            return;
        }
        if (!RECEIPT_IMAGE_TYPES.has(file.type)) {
            event.target.value = '';
            document.getElementById('payment-receipt-url').value = '';
            setReceiptStatus('Only JPG, JPEG, PNG, and WEBP payment receipts are accepted.', 'error');
            updateRegistrationSubmitState();
            return;
        }
        uploadPaymentReceipt(file);
    }
});

document.addEventListener('input', (event) => {
    if (event.target.closest('#codesprint-registration-form')) updateRegistrationSubmitState();
});

document.addEventListener('change', (event) => {
    if (event.target.closest('#codesprint-registration-form')) updateRegistrationSubmitState();
});

document.addEventListener('submit', async (event) => {
    const form = event.target;
    if (form.id !== 'codesprint-registration-form') return;
    event.preventDefault();
    const submitButton = document.getElementById('registration-submit');
    document.getElementById('registration-error').classList.add('hidden');
    if (!form.checkValidity()) {
        form.reportValidity();
        showRegistrationError('Please complete every required field before filing your dossier.');
        return;
    }
    const receiptUrl = document.getElementById('payment-receipt-url').value;
    if (!receiptUrl || document.getElementById('payment-receipt').dataset.uploading === 'true') {
        showRegistrationError('Upload a successful payment receipt before completing registration.');
        updateRegistrationSubmitState();
        return;
    }
    if (form.dataset.submitting === 'true') return;

    form.dataset.submitting = 'true';
    submitButton.disabled = true;
    submitButton.innerHTML = '<i data-lucide="loader-circle" class="w-4 h-4 animate-spin"></i><span>SUBMITTING CASE FILE…</span>';
    if (typeof lucide !== 'undefined') lucide.createIcons();
    try {
        console.info('Submitting CodeSprint registration', {
            fullName: form.elements['entry.1108326818'].value,
            email: form.elements['entry.2062888114'].value,
            college: form.elements['entry.362793320'].value,
            participation: form.elements['entry.856098371'].value,
            receiptUrl,
        });
        // A native form post is required: fetch(no-cors) resolves even when
        // Google rejects the request. The hidden target keeps Google UI out of
        // view while submitting the exact form fields, including receipt URL.
        nativeGoogleSubmissionPending = true;
        form.submit();
    } catch (err) {
        showRegistrationError('Transmission could not be completed. Please check your connection and try again.');
        nativeGoogleSubmissionPending = false;
        form.dataset.submitting = '';
        submitButton.disabled = false;
        submitButton.innerHTML = '<i data-lucide="lock-keyhole" class="w-4 h-4"></i><span>COMPLETE REGISTRATION</span>';
        updateRegistrationSubmitState();
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
});

window.addEventListener('DOMContentLoaded', () => {
    const responseFrame = document.getElementById('googleFormSubmitFrame');
    if (!responseFrame) return;
    responseFrame.addEventListener('load', () => {
        if (!nativeGoogleSubmissionPending) return;
        nativeGoogleSubmissionPending = false;
        const form = getRegistrationForm();
        const submitButton = document.getElementById('registration-submit');
        // Cross-origin restrictions prevent reading Google's response body;
        // importantly, this is now a delivery notification—not a false claim
        // that a Sheet row was created.
        form.reset();
        resetReceiptEvidence();
        updateDuoFields();
        form.dataset.submitting = '';
        submitButton.disabled = true;
        submitButton.innerHTML = '<i data-lucide="lock-keyhole" class="w-4 h-4"></i><span>COMPLETE REGISTRATION</span>';
        document.getElementById('registration-form-panel').classList.add('hidden');
        document.getElementById('registration-success').classList.remove('hidden');
        playClickSound();
        if (typeof lucide !== 'undefined') lucide.createIcons();
    });
});

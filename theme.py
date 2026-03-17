CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Styrene+A+LC:wght@400;500&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;1,400&family=DM+Sans:wght@300;400;500;600&family=Fira+Code:wght@400&display=swap');

:root {
    /* ── Base surfaces (light warm) ── */
    --bg-page:       #faf8f5;
    --bg-surface:    #ffffff;
    --bg-raised:     #fdf6f0;
    --bg-input:      #ffffff;

    /* ── Claude orange-peach palette ── */
    --peach-100:     #fff3ec;
    --peach-200:     #ffe4d0;
    --peach-300:     #ffcfb0;
    --orange-400:    #e8784a;
    --orange-500:    #d4622e;
    --orange-glow:   rgba(232,120,74,0.18);

    /* ── User bubble — warm sand ── */
    --user-bg:       #fdf0e8;
    --user-border:   rgba(232,120,74,0.22);
    --user-text:     #3d2510;

    /* ── Bot bubble — clean white ── */
    --bot-bg:        #ffffff;
    --bot-border:    #ede8e2;
    --bot-text:      #2d2418;

    /* ── Text hierarchy ── */
    --text-heading:  #1a1208;
    --text-body:     #3d3526;
    --text-secondary:#7a6e62;
    --text-muted:    #b0a898;
    --text-link:     var(--orange-400);

    /* ── Borders ── */
    --border-light:  #ede8e2;
    --border-medium: #ddd6cc;
    --border-focus:  var(--orange-400);

    /* ── Shape ── */
    --r-xs:  6px;
    --r-sm:  10px;
    --r-md:  14px;
    --r-lg:  20px;
    --r-xl:  24px;

    /* ── Shadows ── */
    --shadow-sm:    0 1px 4px rgba(60,30,10,0.07);
    --shadow-md:    0 3px 12px rgba(60,30,10,0.09);
    --shadow-focus: 0 0 0 3px rgba(232,120,74,0.18);
}

/* ── Base ── */
*, *::before, *::after { box-sizing: border-box; }

body, .gradio-container {
    background: var(--bg-page) !important;
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text-body) !important;
    -webkit-font-smoothing: antialiased;
}

.gradio-container {
    max-width: 860px !important;
    margin: 0 auto !important;
    padding: 0 !important;
}

footer, .svelte-1ipelgc, .built-with { display: none !important; }

/* ══════════════════════════════════════
   HEADER
══════════════════════════════════════ */
.app-header {
    background: linear-gradient(108deg, #fff8f3 0%, #fdf2ea 100%);
    border-bottom: 1px solid var(--border-light);
    padding: 20px 28px 17px;
    display: flex;
    align-items: center;
    gap: 13px;
    box-shadow: var(--shadow-sm);
}

.header-logo {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, #e8784a, #c95e2a);
    border-radius: var(--r-sm);
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    box-shadow: 0 3px 12px rgba(232,120,74,0.38);
    flex-shrink: 0;
}

.header-title {
    font-family: 'Lora', serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-heading);
    letter-spacing: -0.01em;
    line-height: 1.2;
}

.header-sub {
    font-size: 0.7rem;
    color: var(--text-muted);
    font-weight: 400;
    margin-top: 2px;
    letter-spacing: 0.01em;
}

.header-badge {
    margin-left: auto;
    background: rgba(232,120,74,0.1);
    border: 1px solid rgba(232,120,74,0.28);
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 0.67rem;
    font-weight: 600;
    color: var(--orange-500);
    letter-spacing: 0.07em;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 5px;
}

.header-badge::before {
    content: '';
    width: 5px; height: 5px;
    border-radius: 50%;
    background: var(--orange-400);
    animation: pulse 2.4s ease infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1;   transform: scale(1); }
    50%       { opacity: 0.4; transform: scale(0.8); }
}

/* ══════════════════════════════════════
   CHAT WINDOW
══════════════════════════════════════ */
.chatbot {
    background: var(--bg-page) !important;
    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    padding: 22px 26px 10px !important;
    min-height: 400px !important;
}

@keyframes msgIn {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}

.message-wrap { animation: msgIn 0.2s ease both; }

/* ── User bubble ── */
.message.user {
    background: var(--user-bg) !important;
    border: 1px solid var(--user-border) !important;
    border-radius: var(--r-xl) var(--r-xl) var(--r-xs) var(--r-xl) !important;
    color: var(--user-text) !important;
    max-width: 72% !important;
    margin-left: auto !important;
    padding: 11px 16px !important;
    font-size: 0.875rem !important;
    line-height: 1.65 !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ── Bot bubble ── */
.message.bot {
    background: var(--bot-bg) !important;
    border: 1px solid var(--bot-border) !important;
    border-radius: var(--r-xs) var(--r-xl) var(--r-xl) var(--r-xl) !important;
    color: var(--bot-text) !important;
    max-width: 78% !important;
    margin-right: auto !important;
    padding: 13px 17px !important;
    font-size: 0.875rem !important;
    line-height: 1.78 !important;
    box-shadow: var(--shadow-sm) !important;
}

.message.bot p { margin-bottom: 8px; }
.message.bot p:last-child { margin-bottom: 0; }

.message.bot strong {
    color: var(--orange-500) !important;
    font-weight: 600 !important;
}

.message.bot code {
    background: var(--peach-100) !important;
    border: 1px solid var(--peach-200) !important;
    border-radius: var(--r-xs) !important;
    padding: 1px 6px !important;
    font-family: 'Fira Code', monospace !important;
    font-size: 0.79rem !important;
    color: var(--orange-500) !important;
}

.message.bot hr {
    border: none !important;
    border-top: 1px solid var(--border-light) !important;
    margin: 10px 0 !important;
}

.message.bot ul, .message.bot ol { padding-left: 18px; }
.message.bot li { margin-bottom: 4px; }

.input-row {
    background: var(--bg-surface) !important;
    border-top: 1px solid var(--border-light) !important;
    padding: 13px 20px 15px !important;
    gap: 10px !important;
}

textarea, input[type="text"] {
    background: var(--bg-input) !important;
    border: 1.5px solid var(--border-medium) !important;
    border-radius: var(--r-md) !important;
    color: var(--text-body) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
    padding: 11px 15px !important;
    line-height: 1.55 !important;
    resize: none !important;
    transition: border-color 0.18s, box-shadow 0.18s !important;
    box-shadow: var(--shadow-sm) !important;
}

textarea::placeholder, input[type="text"]::placeholder {
    color: var(--text-muted) !important;
    font-weight: 300 !important;
}

textarea:focus, input[type="text"]:focus {
    border-color: var(--border-focus) !important;
    box-shadow: var(--shadow-focus), var(--shadow-sm) !important;
    outline: none !important;
}

/* Submit */
button.primary {
    background: linear-gradient(135deg, #e8784a, #c95e2a) !important;
    border: none !important;
    border-radius: var(--r-md) !important;
    color: #fff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    padding: 11px 20px !important;
    cursor: pointer !important;
    transition: transform 0.14s, box-shadow 0.14s, opacity 0.14s !important;
    box-shadow: 0 3px 12px rgba(232,120,74,0.38) !important;
    letter-spacing: 0.01em !important;
}

button.primary:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 18px rgba(232,120,74,0.5) !important;
}

button.primary:active { transform: translateY(0) !important; }

/* Secondary */
button.secondary {
    background: transparent !important;
    border: 1px solid var(--border-medium) !important;
    border-radius: var(--r-sm) !important;
    color: var(--text-muted) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.76rem !important;
    padding: 7px 13px !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
}

button.secondary:hover {
    background: var(--peach-100) !important;
    border-color: var(--orange-400) !important;
    color: var(--orange-500) !important;
}

/* ══════════════════════════════════════
   EXAMPLE CHIPS
══════════════════════════════════════ */
.examples-holder, .examples {
    background: var(--bg-surface) !important;
    padding: 4px 24px 16px !important;
    border-top: 1px solid var(--border-light) !important;
}

.examples-holder label, .examples > label {
    font-size: 0.68rem !important;
    color: var(--text-muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.09em !important;
    font-weight: 600 !important;
    margin-bottom: 8px !important;
    display: block !important;
}

.examples table td button {
    background: var(--bg-raised) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: 999px !important;
    color: var(--text-secondary) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.74rem !important;
    padding: 5px 14px !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
    white-space: nowrap !important;
}

.examples table td button:hover {
    border-color: var(--orange-400) !important;
    color: var(--orange-500) !important;
    background: var(--peach-100) !important;
}


.info-strip {
    background: var(--bg-raised);
    border-top: 1px solid var(--border-light);
    padding: 18px 26px 20px;
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}

.icard {
    flex: 1;
    min-width: 145px;
    background: var(--bg-surface);
    border: 1px solid var(--border-light);
    border-radius: var(--r-md);
    padding: 14px 15px;
    display: flex;
    align-items: flex-start;
    gap: 11px;
    transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
    cursor: default;
    box-shadow: var(--shadow-sm);
}

.icard:hover {
    border-color: rgba(232,120,74,0.35);
    box-shadow: 0 4px 16px rgba(232,120,74,0.1);
    transform: translateY(-2px);
}

.icard-icon {
    width: 32px; height: 32px;
    border-radius: var(--r-sm);
    display: flex; align-items: center; justify-content: center;
    font-size: 15px;
    flex-shrink: 0;
}

.icard-icon.a { background: var(--peach-200); }
.icard-icon.b { background: #fce8d4; }
.icard-icon.c { background: #ffeedd; }

.icard-title {
    font-size: 0.71rem;
    font-weight: 700;
    color: var(--text-body);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 3px;
}

.icard-desc {
    font-size: 0.72rem;
    color: var(--text-muted);
    line-height: 1.5;
}


::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: var(--peach-300);
    border-radius: 999px;
}
::-webkit-scrollbar-thumb:hover { background: var(--orange-400); }

@media (max-width: 600px) {
    .app-header { padding: 14px 16px; }
    .chatbot    { padding: 14px 12px 8px !important; }
    .info-strip { padding: 14px 16px; }
    .message.user { max-width: 88% !important; }
    .message.bot  { max-width: 93% !important; }
    .icard        { min-width: 100%; }
    .header-badge { display: none; }
}
"""
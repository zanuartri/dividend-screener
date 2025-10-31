"""UI styling and CSS management."""

import streamlit as st


@st.cache_resource
def get_custom_css():
    """Return cached custom CSS styles for Bloomberg terminal theme."""
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');

:root {
    --bg-primary: #0d0d0d;
    --bg-secondary: #1a1a1a;
    --bg-tertiary: #262626;
    --text-primary: #f5f5f5;
    --text-secondary: #cccccc;
    --text-muted: #808080;
    --border-color: #333333;
    --accent-orange: #ff8c00;
    --accent-green: #00ff41;
    --accent-red: #ff3333;
    --accent-yellow: #ffd700;
    --accent-blue: #00a0ff;
    --font: 'IBM Plex Mono', 'Courier New', monospace;
}

body {
    background-color: var(--bg-primary);
    color: var(--text-primary);
    font-family: var(--font);
}

.main .block-container {
    max-width: 2000px;
    padding: 0.2rem 1rem 0.5rem 1rem;
    padding-top: 0.2rem !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: var(--font);
    text-transform: uppercase;
    letter-spacing: 2px;
    font-weight: 700;
}

h1 {
    font-size: 1.5rem;
    color: var(--accent-orange);
    margin-bottom: 0;
    text-shadow: 0 0 10px rgba(255, 140, 0, 0.3);
}

h3 {
    font-size: 0.95rem;
    color: var(--text-secondary);
    margin: 1rem 0 0.5rem 0;
}

hr {
    border-top: 1px solid var(--border-color);
    margin: 0.5rem 0;
}

/* Bloomberg-style data box */
.bbg-box {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    padding: 12px;
    border-radius: 2px;
    height: 100%;
}

.bbg-label {
    font-size: 9px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
}

.bbg-value {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 2px;
}

.bbg-status {
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
}

.status-strong { color: var(--accent-green); border-left: 3px solid var(--accent-green); padding-left: 8px; }
.status-good { color: #90ee90; border-left: 3px solid #90ee90; padding-left: 8px; }
.status-moderate { color: var(--accent-yellow); border-left: 3px solid var(--accent-yellow); padding-left: 8px; }
.status-weak { color: var(--accent-red); border-left: 3px solid var(--accent-red); padding-left: 8px; }

/* Info box */
.info-box {
    background: var(--bg-secondary);
    border-left: 4px solid var(--accent-orange);
    padding: 12px 16px;
    margin: 10px 0;
    font-size: 11px;
    line-height: 1.6;
    min-height: 300px;
}

.info-box strong {
    color: var(--accent-orange);
}

/* Calendar styling */
.month-block {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 2px;
    padding: 12px;
    height: 280px;
    margin-bottom: 15px;
    transition: all 0.2s;
}

.month-block:hover {
    border-color: var(--accent-orange);
    box-shadow: 0 0 10px rgba(255, 140, 0, 0.2);
}

.month-block.current {
    border-color: var(--accent-orange);
    border-width: 2px;
    background: linear-gradient(to bottom, #1a1a1a, var(--bg-secondary));
}

.month-title {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--accent-orange);
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 8px;
}

.month-title .count {
    font-size: 10px;
    background: var(--accent-orange);
    color: var(--bg-primary);
    padding: 2px 8px;
    border-radius: 2px;
    font-weight: 700;
}

.ticker-list {
    overflow-y: auto;
    flex-grow: 1;
    max-height: 220px;
}

.ticker-item {
    display: flex;
    justify-content: space-between;
    padding: 6px 4px;
    border-bottom: 1px solid #2a2a2a;
    font-size: 11px;
}

.ticker-item:last-child {
    border-bottom: none;
}

.ticker-item:hover {
    background: var(--bg-tertiary);
}

.ticker-name {
    color: var(--text-primary);
    font-weight: 700;
    letter-spacing: 1px;
}

.ticker-type {
    color: var(--text-muted);
    text-transform: uppercase;
    font-size: 9px;
}

.no-dividends {
    text-align: center;
    color: var(--text-muted);
    margin-top: 40px;
    font-style: italic;
    font-size: 10px;
}

/* Compact tables */
[data-testid="stDataFrame"] {
    font-size: 11px;
    font-family: var(--font);
}

[data-testid="stDataFrame"] .col-header {
    background: var(--bg-tertiary);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
}

[data-testid="stDataFrame"] tbody tr:hover {
    background: rgba(255, 140, 0, 0.15) !important;
    cursor: pointer;
}

[data-testid="stDataFrame"] tbody tr.selected {
    background: rgba(255, 140, 0, 0.25) !important;
    border-left: 3px solid var(--accent-orange) !important;
}

[data-testid="stDataFrame"] tbody td {
    border-bottom: 1px solid var(--border-color) !important;
}

/* Expander styling - Remove double border issue */
[data-testid="stExpander"] {
    background: transparent;
    border: none !important;
    border-radius: 0;
}

[data-testid="stExpander"] > details {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 2px;
}

[data-testid="stExpander"] summary {
    font-family: var(--font);
    text-transform: uppercase;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    color: var(--text-primary);
    transition: color 0.2s;
    padding: 12px 16px;
    display: flex !important;
    flex-direction: row !important;
    justify-content: space-between !important;
    align-items: center !important;
    cursor: pointer;
}

[data-testid="stExpander"] summary:hover {
    color: var(--accent-orange);
    background: var(--bg-tertiary);
}

/* Ensure icon stays on the right */
[data-testid="stExpander"] summary svg {
    fill: var(--accent-orange);
    transition: fill 0.2s;
    order: 2 !important;
    margin-left: auto !important;
    margin-right: 0 !important;
}

/* Ensure text stays on the left */
[data-testid="stExpander"] summary > div {
    order: 1 !important;
    flex-grow: 1 !important;
}

[data-testid="stExpander"] summary:hover svg {
    fill: var(--accent-orange);
    filter: drop-shadow(0 0 5px rgba(255, 140, 0, 0.5));
}

/* Expander content padding */
[data-testid="stExpander"] details > div {
    padding: 12px 16px !important;
    border-top: 1px solid var(--border-color);
}

/* Buttons - Bloomberg style */
.stButton>button {
    background: linear-gradient(to bottom, var(--bg-tertiary), var(--bg-secondary));
    border: 2px solid var(--accent-orange);
    color: var(--accent-orange);
    font-family: var(--font);
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    padding: 10px 20px;
    border-radius: 0px;
    transition: all 0.2s;
    box-shadow: 0 0 10px rgba(255, 140, 0, 0.2);
}

.stButton>button:hover {
    background: var(--accent-orange);
    color: var(--bg-primary);
    box-shadow: 0 0 20px rgba(255, 140, 0, 0.5);
}

/* Inputs */
.stTextInput>div>div>input, .stNumberInput>div>div>input {
    background: #1a1a1a !important;
    border: 1px solid #444444 !important;
    border-radius: 3px !important;
    color: var(--text-primary) !important;
    font-family: var(--font);
    font-size: 11px;
    padding: 8px 12px !important;
    transition: all 0.2s !important;
}

/* Ensure select outer wrapper doesn't fight our inner control styling */
.stSelectbox>div>div,
.stMultiSelect>div>div {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

/* Number Input wrapper */
.stNumberInput {
    position: relative !important;
    margin: 3px 0 !important;
}

/* Number Input - use darker background for visibility */
.stNumberInput [data-baseweb="input"] {
    background: #0d0d0d !important;
    border: 1px solid #444444 !important;
    border-radius: 3px !important;
    transition: all 0.2s !important;
    min-height: 42px !important;
    height: 42px !important;
    box-sizing: border-box !important;
}

.stNumberInput [data-baseweb="input"] > div {
    min-height: 40px !important;
    height: 40px !important;
    display: flex !important;
    align-items: center !important;
    padding: 0 !important;
    margin: 0 !important;
}

.stNumberInput [data-baseweb="input"]:hover {
    background: #151515 !important;
    border-color: #555555 !important;
}

.stNumberInput [data-baseweb="input"]:focus-within {
    background: #1a1a1a !important;
    border-color: var(--accent-orange) !important;
    box-shadow: 0 0 0 1px var(--accent-orange) !important;
}

/* Number input field itself */
.stNumberInput input[type="number"] {
    background: transparent !important;
    border: none !important;
    color: var(--text-primary) !important;
    font-family: var(--font) !important;
    font-size: 11px !important;
    padding: 0 12px !important;
    height: 100% !important;
    flex: 1 !important;
    margin: 0 !important;
}

/* Hide default spinners */
.stNumberInput input[type="number"]::-webkit-inner-spin-button,
.stNumberInput input[type="number"]::-webkit-outer-spin-button {
    -webkit-appearance: none !important;
    margin: 0 !important;
}

.stNumberInput input[type="number"] {
    -moz-appearance: textfield !important;
}

/* Number Input buttons (+/-) */
.stNumberInput button {
    background: transparent !important;
    border: none !important;
    color: var(--accent-orange) !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 0 !important;
    min-width: 32px !important;
    width: 32px !important;
    height: 40px !important;
    flex-shrink: 0 !important;
    margin: 0 !important;
}

.stNumberInput button:hover {
    background: rgba(255, 140, 0, 0.1) !important;
    color: #fff !important;
}

/* Input focus state */
.stTextInput>div>div>input:focus,
.stNumberInput>div>div>input:focus {
    background: transparent !important;
    border: none !important;
    outline: none !important;
}

/* Selectbox styling - unify with number input look */
.stSelectbox [data-baseweb="select"] {
    background: #0d0d0d !important; /* match number input */
    border: 1px solid #444444 !important;
    border-radius: 3px !important;
    transition: all 0.2s !important;
    min-height: 42px !important;
}

/* Deep select internals to ensure background stays consistent */
.stSelectbox [data-baseweb="select"] > div,
.stSelectbox [data-baseweb="select"] div[data-baseweb="value-container"],
.stSelectbox [data-baseweb="select"] div[role="combobox"],
.stSelectbox [data-baseweb="select"] input {
    background: #0d0d0d !important;
    color: var(--text-primary) !important;
}

.stSelectbox [data-baseweb="select"]:hover {
    background: #151515 !important; /* match hover of number input */
    border-color: #555555 !important;
}

.stSelectbox [data-baseweb="select"]:focus-within {
    background: #1a1a1a !important; /* match focus of number input */
    border-color: var(--accent-orange) !important;
    box-shadow: 0 0 0 1px var(--accent-orange) !important;
}

/* Multiselect styling - unify with number input look */
.stMultiSelect [data-baseweb="select"] {
    background: #0d0d0d !important; /* match number input */
    border: 1px solid #444444 !important;
    border-radius: 3px !important;
    transition: all 0.2s !important;
    min-height: 42px !important;
}

/* Deep multiselect internals to ensure background stays consistent */
.stMultiSelect [data-baseweb="select"] > div,
.stMultiSelect [data-baseweb="select"] div[data-baseweb="value-container"],
.stMultiSelect [data-baseweb="select"] div[role="combobox"],
.stMultiSelect [data-baseweb="select"] input {
    background: #0d0d0d !important;
    color: var(--text-primary) !important;
}

.stMultiSelect [data-baseweb="select"]:hover {
    background: #151515 !important;
    border-color: #555555 !important;
}

.stMultiSelect [data-baseweb="select"]:focus-within {
    background: #1a1a1a !important;
    border-color: var(--accent-orange) !important;
    box-shadow: 0 0 0 1px var(--accent-orange) !important;
}

.stMultiSelect [data-baseweb="tag"] {
    background: var(--accent-orange) !important;
    color: #000 !important;
    border-radius: 2px !important;
    font-size: 10px !important;
    font-weight: 600 !important;
}

.stMultiSelect [data-baseweb="tag"] svg {
    fill: #000 !important;
}

/* Hide "Press Enter to submit form" hint */
.stTextInput>div>div>input::placeholder,
.stNumberInput>div>div>input::placeholder {
    color: #666 !important;
}

.stForm [data-testid="InputInstructions"] {
    display: none !important;
}

/* Selectbox specific - fix text truncation */
.stSelectbox [data-baseweb="select"] {
    min-height: 42px !important;
}

.stSelectbox [data-baseweb="select"] > div {
    min-height: 42px !important;
    padding: 10px 12px !important;
    align-items: center !important;
}

.stSelectbox [data-baseweb="select"] > div > div {
    line-height: 20px !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}

.stSelectbox [data-baseweb="select"] span,
.stSelectbox [data-baseweb="select"] div[data-baseweb="base-input"] {
    font-size: 11px !important;
    line-height: 20px !important;
}

/* Dropdown options */
[data-baseweb="popover"] {
    font-family: var(--font) !important;
}

[role="option"] {
    font-size: 11px !important;
    padding: 10px 12px !important;
    line-height: 20px !important;
    min-height: 40px !important;
}

/* Placeholder and text color consistency */
.stSelectbox [data-baseweb="select"] ::placeholder,
.stMultiSelect [data-baseweb="select"] ::placeholder {
    color: #666 !important;
}

.stTextInput>div>div>input:focus, .stSelectbox>div>div:focus-within, .stNumberInput>div>div>input:focus {
    border-color: var(--accent-orange) !important;
    box-shadow: 0 0 0 1px var(--accent-orange) !important;
    outline: none !important;
}

.stMultiSelect>div>div {
    background: #0d0d0d !important; /* align with other inputs */
    font-family: var(--font);
    font-size: 11px;
}

/* Tabs - Bloomberg orange accent */
[data-testid="stTabs"] button {
    /* Add emoji-capable fallbacks so icons like 📊 📅 render correctly */
    font-family: 'IBM Plex Mono', 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 'Segoe UI Symbol', 'Courier New', monospace;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--text-muted);
    background: var(--bg-secondary);
    border: none;
    padding: 12px 24px;
    line-height: 1.2;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

[data-testid="stTabs"] button:hover {
    color: var(--text-primary);
    background: var(--bg-tertiary);
}

[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--accent-orange);
    border-bottom: 3px solid var(--accent-orange);
    background: var(--bg-primary);
}

/* Dialog */
[data-baseweb="dialog"] {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
}

/* Make dialog wider and ensure it starts from top */
[data-testid="stDialog"] {
    width: 100% !important;
    display: flex !important;
    align-items: flex-start !important;
    padding-top: 2rem !important;
}

[data-testid="stDialog"] > div {
    width: 100% !important;
    margin-top: 0 !important;
}

/* Preview Panel - Override Streamlit defaults */
.preview-card {
    background: #1a1a1a !important;
    padding: 16px !important;
    border-left: 3px solid #ff8c00 !important;
    margin: 0 !important;
}

.preview-header {
    display: flex !important;
    justify-content: space-between !important;
    align-items: baseline !important;
    margin-bottom: 16px !important;
    border-bottom: 1px solid #333 !important;
    padding-bottom: 8px !important;
}

.preview-ticker {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #ff8c00 !important;
    letter-spacing: 1px !important;
}

.preview-price {
    font-size: 18px !important;
    font-weight: 700 !important;
    color: #fff !important;
}

.preview-metrics {
    display: grid !important;
    grid-template-columns: 1fr 1fr !important;
    gap: 12px !important;
    margin-bottom: 12px !important;
}

.preview-metric-row {
    display: flex !important;
    justify-content: space-between !important;
}

.preview-label {
    font-size: 9px !important;
    color: #808080 !important;
    letter-spacing: 1px !important;
}

.preview-value {
    font-size: 11px !important;
    font-weight: 700 !important;
}

.preview-value-orange {
    color: #ff8c00 !important;
}

.preview-value-white {
    color: #fff !important;
}

.preview-signal-box {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    padding: 8px !important;
    background: #0d0d0d !important;
    margin-top: 0 !important;
}

.preview-fair-value-box {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    padding: 8px !important;
    margin-top: 4px !important;
    background: #0d0d0d !important;
}

/* Calendar Cards - Override Streamlit defaults */
.calendar-card {
    background: #1a1a1a !important;
    padding: 12px !important;
    margin-bottom: 8px !important;
}

.calendar-header {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    margin-bottom: 8px !important;
    padding-bottom: 8px !important;
    border-bottom: 1px solid #333 !important;
}

.calendar-month {
    font-size: 12px !important;
    font-weight: 700 !important;
    color: #ff8c00 !important;
}

.calendar-count {
    font-size: 11px !important;
    font-weight: 700 !important;
    color: #666 !important;
}

.calendar-stock-item {
    display: flex !important;
    justify-content: space-between !important;
    padding: 6px 0 !important;
    border-bottom: 1px solid #262626 !important;
}

.calendar-ticker {
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #fff !important;
}

.calendar-type {
    font-size: 9px !important;
    color: #808080 !important;
}

.calendar-empty {
    padding: 12px !important;
    text-align: center !important;
    color: #666 !important;
    font-size: 10px !important;
}

</style>
"""


def get_loading_skeleton():
    """Return HTML for animated loading skeleton."""
    return """
    <div style='background: #1a1a1a; padding: 20px; border-radius: 4px; border: 1px solid #333; margin: 20px 0;'>
        <div style='font-size: 16px; color: #ff8c00; font-weight: 700; margin-bottom: 10px; font-family: "IBM Plex Mono", monospace;'>
            ⚡ LOADING MARKET DATA
        </div>
        <div style='font-size: 11px; color: #808080; margin-bottom: 15px; font-family: "IBM Plex Mono", monospace;'>
            Fetching real-time prices for 36 stocks...
        </div>
        <div style='background: #0d0d0d; height: 8px; border-radius: 4px; overflow: hidden; position: relative;'>
            <div style='
                position: absolute;
                height: 100%;
                background: linear-gradient(90deg, #ff8c00, #ffa500, #ff8c00);
                background-size: 200% 100%;
                animation: loading 1.5s ease-in-out infinite;
                width: 60%;
            '></div>
        </div>
        <style>
            @keyframes loading {
                0% { transform: translateX(-100%); }
                50% { transform: translateX(50%); }
                100% { transform: translateX(150%); }
            }
        </style>
    </div>
    """

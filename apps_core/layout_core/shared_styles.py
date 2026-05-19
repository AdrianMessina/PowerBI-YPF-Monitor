"""
YPF BI Monitor - Shared Styles Module
Design System: Industrial Data Precision
Typography: Fira Sans (body) + Fira Code (code/DAX)
Palette: YPF Blue #0451E4 / Slate dark sidebar / Light content
"""
import streamlit as st
from pathlib import Path


# Design Tokens (Python access)
YPF_BLUE = "#0451E4"
YPF_BLUE_DARK = "#0340B8"
YPF_BLUE_DEEPER = "#022A8A"
YPF_BLACK = "#000000"
YPF_WHITE = "#FFFFFF"
YPF_GRAY_BG = "#F8FAFC"
YPF_GRAY_TEXT = "#64748B"
YPF_TEXT_DARK = "#0F172A"
YPF_TEXT_SECONDARY = "#475569"
YPF_BORDER = "#E2E8F0"
YPF_BORDER_LIGHT = "#F1F5F9"


def get_shared_css():
    """Return the unified YPF corporate CSS - Industrial Data Precision."""
    return """
    <style>
    /* ============================================================
       YPF BI Monitor — Industrial Data Precision Design System
       Aesthetic: Clean technical precision, dark sidebar contrast,
       subtle depth layers, monochrome + blue accent.
       Fonts: Fira Sans 300-700 / Fira Code 400-600
       ============================================================ */

    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Fira+Sans:wght@300;400;500;600;700&display=swap');

    /* ---- Custom Properties ---- */
    :root {
        /* Brand */
        --blue: #0451E4;
        --blue-hover: #0340B8;
        --blue-deep: #022A8A;
        --blue-glow: rgba(4,81,228,0.14);
        --blue-subtle: rgba(4,81,228,0.05);

        /* Surfaces */
        --surface-0: #FFFFFF;
        --surface-1: #F8FAFC;
        --surface-2: #F1F5F9;
        --surface-3: #E2E8F0;
        --dark-0: #0B1120;
        --dark-1: #0F172A;
        --dark-2: #1E293B;
        --dark-3: #334155;

        /* Text */
        --ink: #0F172A;
        --ink-2: #1E293B;
        --ink-3: #4B5563;
        --ink-4: #6B7280;
        --ink-on-dark: #CBD5E1;
        --ink-white: #F1F5F9;

        /* Borders */
        --line: #E2E8F0;
        --line-light: #F1F5F9;
        --line-dark: rgba(255,255,255,0.07);

        /* Status */
        --green: #059669;
        --amber: #D97706;
        --red: #DC2626;
        --cyan: #0891B2;

        /* Radii */
        --r-sm: 6px;
        --r-md: 8px;
        --r-lg: 12px;
        --r-xl: 16px;
        --r-full: 9999px;

        /* Shadows */
        --sh-xs: 0 1px 2px rgba(0,0,0,0.04);
        --sh-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
        --sh-md: 0 4px 12px rgba(0,0,0,0.07);
        --sh-lg: 0 10px 28px rgba(0,0,0,0.10);
        --sh-blue: 0 4px 20px rgba(4,81,228,0.15);
        --sh-card-hover: 0 8px 24px rgba(4,81,228,0.10), 0 2px 8px rgba(0,0,0,0.06);

        /* Motion */
        --ease: cubic-bezier(0.25, 0.46, 0.45, 0.94);
        --t-fast: 120ms;
        --t-norm: 200ms;
        --t-slow: 320ms;

        /* Fonts */
        --sans: 'Fira Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        --mono: 'Fira Code', 'Cascadia Code', 'Consolas', monospace;
    }

    /* ---- Reduced Motion ---- */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }
    }

    /* ---- Base Typography ---- */
    html, body, [class*="css"] {
        font-family: var(--sans) !important;
        color: var(--ink);
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    code, pre, .stCodeBlock, [data-testid="stCode"] {
        font-family: var(--mono) !important;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: var(--sans) !important;
        color: var(--ink);
        letter-spacing: -0.025em;
        line-height: 1.25;
    }
    h1 { font-weight: 700; font-size: 1.6rem; }
    h2 { font-weight: 600; font-size: 1.2rem; }
    h3 { font-weight: 600; font-size: 1.05rem; }
    p  { line-height: 1.65; color: var(--ink-2); font-size: 0.92rem; }
    li { line-height: 1.65; color: var(--ink-2); font-size: 0.88rem; }
    strong { color: var(--ink); }

    /* ============================================================
       HEADER
       ============================================================ */
    .ypf-header {
        background: var(--dark-1);
        padding: 1.25rem 1.75rem 1rem;
        border-radius: var(--r-lg);
        margin-bottom: 1.25rem;
        position: relative;
        overflow: hidden;
    }
    /* Blue accent line across the top */
    .ypf-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--blue) 0%, var(--blue-hover) 40%, transparent 80%);
    }
    /* Subtle grid texture */
    .ypf-header::after {
        content: '';
        position: absolute;
        inset: 0;
        background-image:
            linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
        background-size: 32px 32px;
        pointer-events: none;
    }
    .ypf-header h1 {
        color: var(--ink-white);
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.03em;
        position: relative;
        z-index: 1;
    }
    .ypf-header .subtitle {
        color: var(--ink-on-dark);
        font-size: 0.88rem;
        margin: 0.35rem 0 0 0;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    .ypf-header .version {
        display: inline-block;
        color: var(--blue);
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        background: rgba(4,81,228,0.12);
        padding: 0.2rem 0.65rem;
        border-radius: var(--r-full);
        margin-top: 0.6rem;
        position: relative;
        z-index: 1;
    }

    /* ============================================================
       SECTION HEADERS
       ============================================================ */
    .section-header {
        background: var(--surface-1);
        border-left: 3px solid var(--blue);
        padding: 0.55rem 1rem;
        font-weight: 600;
        font-size: 0.88rem;
        color: var(--ink);
        margin: 1.25rem 0 0.65rem 0;
        border-radius: 0 var(--r-sm) var(--r-sm) 0;
    }

    /* ============================================================
       HELP / INFO BOXES
       ============================================================ */
    .help-box {
        background: var(--blue-subtle);
        border-left: 3px solid var(--blue);
        padding: 1rem 1.25rem;
        border-radius: 0 var(--r-sm) var(--r-sm) 0;
        margin: 0.75rem 0;
    }
    .help-box h4 {
        font-size: 0.88rem;
        margin: 0 0 0.4rem 0;
        color: var(--ink);
    }
    .help-box ul { margin: 0; padding-left: 1.15rem; }
    .help-box li { font-size: 0.84rem; margin-bottom: 0.2rem; }

    /* ============================================================
       BUTTONS
       ============================================================ */
    .stButton > button,
    .stDownloadButton > button {
        background: var(--blue) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--r-sm) !important;
        font-weight: 600 !important;
        font-family: var(--sans) !important;
        font-size: 0.87rem !important;
        letter-spacing: 0.01em !important;
        padding: 0.5rem 1.25rem !important;
        transition: background var(--t-norm) var(--ease),
                    box-shadow var(--t-norm) var(--ease),
                    transform var(--t-fast) var(--ease) !important;
        cursor: pointer !important;
    }
    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: var(--blue-hover) !important;
        box-shadow: var(--sh-blue) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button:active,
    .stDownloadButton > button:active {
        transform: translateY(0) !important;
        box-shadow: var(--sh-xs) !important;
    }
    /* Focus ring */
    .stButton > button:focus-visible,
    .stDownloadButton > button:focus-visible {
        outline: 2px solid var(--blue) !important;
        outline-offset: 2px !important;
    }

    /* ============================================================
       EXPANDERS
       ============================================================ */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 0.9rem;
        color: var(--ink);
        cursor: pointer !important;
        transition: color var(--t-fast) var(--ease);
    }
    .streamlit-expanderHeader:hover { color: var(--blue); }

    /* ============================================================
       METRIC CARDS
       ============================================================ */
    [data-testid="stMetric"] {
        background: var(--surface-0);
        border: 1px solid var(--line);
        border-radius: var(--r-md);
        padding: 1rem 1.2rem;
        box-shadow: var(--sh-xs);
        transition: box-shadow var(--t-norm) var(--ease),
                    border-color var(--t-norm) var(--ease);
        position: relative;
        overflow: hidden;
    }
    [data-testid="stMetric"]::after {
        content: '';
        position: absolute;
        top: 0; left: 0; bottom: 0;
        width: 3px;
        background: var(--blue);
    }
    [data-testid="stMetric"]:hover {
        box-shadow: var(--sh-blue);
        border-color: rgba(4,81,228,0.18);
    }
    [data-testid="stMetricValue"] {
        color: var(--blue) !important;
        font-weight: 700 !important;
        font-family: var(--sans) !important;
        font-size: 1.45rem !important;
        letter-spacing: -0.02em !important;
    }
    [data-testid="stMetricLabel"] {
        color: var(--ink-3) !important;
        font-weight: 500 !important;
        font-size: 0.72rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.75rem !important;
    }

    /* ============================================================
       DATA TABLES
       ============================================================ */
    [data-testid="stDataFrame"] table {
        font-family: var(--sans) !important;
        font-size: 0.84rem;
    }
    [data-testid="stDataFrame"] th {
        background: var(--dark-1) !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 0.72rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.6rem 0.75rem !important;
    }
    [data-testid="stDataFrame"] td {
        padding: 0.5rem 0.75rem !important;
        border-bottom: 1px solid var(--line-light) !important;
    }
    [data-testid="stDataFrame"] tr:hover td {
        background: var(--blue-subtle) !important;
    }

    /* ============================================================
       TABS
       ============================================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid var(--line);
    }
    .stTabs [data-baseweb="tab"] {
        font-family: var(--sans) !important;
        font-weight: 500;
        font-size: 0.86rem;
        color: var(--ink-4);
        padding: 0.65rem 1.2rem;
        transition: color var(--t-fast) var(--ease),
                    background var(--t-fast) var(--ease);
        cursor: pointer;
        border-bottom: 2px solid transparent;
        margin-bottom: -1px;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--blue);
        background: var(--blue-subtle);
    }
    .stTabs [aria-selected="true"] {
        color: var(--blue) !important;
        font-weight: 600;
        border-bottom-color: var(--blue) !important;
    }

    /* ============================================================
       FORM INPUTS
       ============================================================ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        font-family: var(--sans) !important;
        font-size: 0.9rem;
        border: 1px solid var(--line);
        border-radius: var(--r-sm);
        transition: border-color var(--t-fast) var(--ease),
                    box-shadow var(--t-fast) var(--ease);
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 3px var(--blue-glow) !important;
    }
    .stSelectbox [data-baseweb="select"] {
        font-family: var(--sans) !important;
        cursor: pointer;
    }
    .stSelectbox [data-baseweb="select"] > div {
        border-radius: var(--r-sm);
        transition: border-color var(--t-fast) var(--ease);
    }
    .stRadio [data-baseweb="radio"],
    .stCheckbox { cursor: pointer !important; }

    /* ============================================================
       FEATURE CARDS (Home)
       ============================================================ */
    .feature-card {
        background: var(--surface-0);
        border: 1px solid var(--line);
        padding: 1rem 1.25rem 0.85rem;
        border-radius: var(--r-md);
        box-shadow: var(--sh-xs);
        margin: 0.35rem 0;
        transition: box-shadow var(--t-norm) var(--ease),
                    border-color var(--t-norm) var(--ease),
                    transform var(--t-norm) var(--ease);
        cursor: default;
        position: relative;
    }
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; bottom: 0;
        width: 3px;
        background: var(--blue);
        border-radius: var(--r-md) 0 0 var(--r-md);
        opacity: 0.6;
        transition: opacity var(--t-norm) var(--ease);
    }
    .feature-card:hover {
        box-shadow: var(--sh-card-hover);
        border-color: rgba(4,81,228,0.12);
        transform: translateY(-2px);
    }
    .feature-card:hover::before { opacity: 1; }
    .feature-card .card-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 40px; height: 40px;
        border-radius: var(--r-sm);
        background: var(--blue-subtle);
        border: 1px solid rgba(4,81,228,0.08);
        margin-bottom: 0.5rem;
        font-size: 1.5rem;
        line-height: 1;
    }
    .feature-card h3 {
        color: var(--ink);
        font-size: 0.98rem;
        font-weight: 600;
        margin: 0 0 0.35rem 0;
        letter-spacing: -0.015em;
    }
    .feature-card p {
        color: var(--ink-3);
        font-size: 0.82rem;
        margin: 0;
        line-height: 1.55;
    }
    .feature-card ul {
        color: var(--ink-3);
        font-size: 0.78rem;
        margin: 0.35rem 0 0 0;
        padding-left: 1rem;
        line-height: 1.55;
    }
    .feature-card li::marker { color: var(--blue); }

    /* ============================================================
       HOME HERO STATS
       ============================================================ */
    .hero-stat {
        text-align: center;
        padding: 1rem 0.5rem;
    }
    .hero-stat .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--blue);
        letter-spacing: -0.03em;
        line-height: 1;
    }
    .hero-stat .stat-label {
        font-size: 0.72rem;
        font-weight: 500;
        color: var(--ink-4);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-top: 0.35rem;
    }

    /* ============================================================
       PBIP INPUT SECTION
       ============================================================ */
    .pbip-input-section {
        background: var(--blue-subtle);
        border: 1px solid var(--line);
        border-left: 3px solid var(--blue);
        border-radius: 0 var(--r-md) var(--r-md) 0;
        padding: 1rem;
        margin: 1rem 0;
    }

    /* ============================================================
       LOADER + SKELETON
       ============================================================ */
    .ypf-loader-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 2.5rem;
    }
    .ypf-loader {
        width: 36px; height: 36px;
        border: 3px solid var(--line);
        border-top-color: var(--blue);
        border-radius: 50%;
        animation: ypf-spin 0.75s linear infinite;
    }
    @keyframes ypf-spin {
        to { transform: rotate(360deg); }
    }
    .ypf-loader-text {
        color: var(--ink-4);
        margin-top: 0.75rem;
        font-size: 0.84rem;
    }

    .skeleton {
        background: linear-gradient(90deg, var(--line) 25%, var(--surface-2) 50%, var(--line) 75%);
        background-size: 200% 100%;
        animation: sk-pulse 1.5s ease-in-out infinite;
        border-radius: var(--r-sm);
        height: 0.9rem;
        margin: 0.45rem 0;
    }
    .skeleton-card {
        background: var(--surface-0);
        border: 1px solid var(--line);
        border-radius: var(--r-md);
        padding: 1.5rem;
        box-shadow: var(--sh-xs);
    }
    .skeleton-card .skeleton-title { height: 1.3rem; width: 55%; margin-bottom: 0.9rem; }
    .skeleton-card .skeleton-text { width: 85%; }
    .skeleton-card .skeleton-text:last-child { width: 60%; }
    @keyframes sk-pulse {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }

    /* ============================================================
       STATUS DOTS
       ============================================================ */
    .status-dot {
        display: inline-block;
        width: 7px; height: 7px;
        border-radius: 50%;
        margin-right: 6px;
    }
    .status-dot.active  { background: var(--green); }
    .status-dot.warning { background: var(--amber); }
    .status-dot.error   { background: var(--red); }

    /* ============================================================
       MISC
       ============================================================ */
    hr {
        border: none;
        border-top: 1px solid var(--line);
        margin: 1.5rem 0;
    }

    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--surface-3); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--ink-4); }

    .ypf-footer {
        text-align: center;
        color: var(--ink-3);
        font-size: 0.7rem;
        border-top: 1px solid var(--line);
        padding-top: 0.75rem;
        margin-top: 2rem;
        font-family: var(--sans);
        letter-spacing: 0.015em;
    }

    .stProgress > div > div > div {
        background: var(--blue) !important;
    }

    .stAlert {
        border-radius: var(--r-md) !important;
        font-family: var(--sans) !important;
        font-size: 0.87rem !important;
    }

    /* ============================================================
       SCROLL-DRIVEN ANIMATIONS (CSS native)
       Uses animation-timeline: view() for viewport-triggered reveals.
       Graceful degradation: elements visible by default,
       animations enhance only on supported browsers.
       ============================================================ */

    /* Keyframes */
    @keyframes scroll-fade-up {
        from {
            opacity: 0;
            transform: translateY(24px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes scroll-fade-in {
        from { opacity: 0; }
        to   { opacity: 1; }
    }

    @keyframes scroll-scale-in {
        from {
            opacity: 0;
            transform: scale(0.96);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }

    /* Apply to elements only when scroll-timeline is supported */
    @supports (animation-timeline: view()) {

        /* Feature cards: slide up as they enter viewport */
        .feature-card {
            animation: scroll-fade-up linear both;
            animation-timeline: view();
            animation-range: entry 0% entry 35%;
        }

        /* Hero stats: fade in */
        .hero-stat {
            animation: scroll-fade-up linear both;
            animation-timeline: view();
            animation-range: entry 0% entry 30%;
        }

        /* Metric cards: scale in */
        [data-testid="stMetric"] {
            animation: scroll-scale-in linear both;
            animation-timeline: view();
            animation-range: entry 0% entry 30%;
        }

        /* Header: subtle fade */
        .ypf-header {
            animation: scroll-fade-in linear both;
            animation-timeline: view();
            animation-range: entry 0% entry 20%;
        }

        /* Section headers: slide up */
        .section-header {
            animation: scroll-fade-up linear both;
            animation-timeline: view();
            animation-range: entry 0% entry 30%;
        }

        /* Help boxes */
        .help-box {
            animation: scroll-fade-up linear both;
            animation-timeline: view();
            animation-range: entry 0% entry 30%;
        }

        /* PBIP sections */
        .pbip-input-section {
            animation: scroll-fade-up linear both;
            animation-timeline: view();
            animation-range: entry 0% entry 30%;
        }

        /* Tables */
        [data-testid="stDataFrame"] {
            animation: scroll-fade-in linear both;
            animation-timeline: view();
            animation-range: entry 0% entry 25%;
        }

        /* Charts (plotly, matplotlib) */
        [data-testid="stPlotlyChart"],
        [data-testid="stImage"],
        .stPlotlyChart {
            animation: scroll-fade-up linear both;
            animation-timeline: view();
            animation-range: entry 0% entry 30%;
        }

        /* Footer: gentle fade */
        .ypf-footer {
            animation: scroll-fade-in linear both;
            animation-timeline: view();
            animation-range: entry 0% entry 40%;
        }
    }

    /* ---- Reduced Motion Override ---- */
    @media (prefers-reduced-motion: reduce) {
        .feature-card,
        .hero-stat,
        [data-testid="stMetric"],
        .ypf-header,
        .section-header,
        .help-box,
        .pbip-input-section,
        [data-testid="stDataFrame"],
        [data-testid="stPlotlyChart"],
        [data-testid="stImage"],
        .stPlotlyChart,
        .ypf-footer {
            animation: none !important;
        }
    }
    </style>
    """


def render_app_header(title: str, subtitle: str = "", version: str = ""):
    """Render a standardized YPF corporate app header with logo."""
    from pathlib import Path

    # Buscar logo
    logo_path = Path(__file__).parent.parent.parent / "assets" / "logo_ypf.png"

    # Crear layout con logo y título
    col1, col2 = st.columns([1, 9])

    with col1:
        if logo_path.exists():
            st.image(str(logo_path), width=80)

    with col2:
        version_html = f'<span class="version">v{version}</span>' if version else ''
        subtitle_html = f'<p class="subtitle">{subtitle}</p>' if subtitle else ''

        st.markdown(f"""
        <div class="ypf-header" style="margin-top: 0.5rem;">
            <h1>{title}</h1>
            {subtitle_html}
            {version_html}
        </div>
        """, unsafe_allow_html=True)


def render_footer():
    """Render a standardized YPF footer with DAIA logo."""
    from pathlib import Path

    # Logo DAIA
    logo_daia_path = Path(__file__).parent.parent.parent / "assets" / "logo_daia.png"

    st.markdown("""
    <div class="ypf-footer" style="text-align: center;">
        Para YPF - Gerencia Visualización - DAIA
    </div>
    """, unsafe_allow_html=True)

    # Logo DAIA centrado debajo del texto
    if logo_daia_path.exists():
        _, col2, _ = st.columns([2, 1, 2])
        with col2:
            st.image(str(logo_daia_path), width=150)


def render_skeleton(rows: int = 3):
    """Render a skeleton loading placeholder."""
    skeleton_rows = ''.join(
        f'<div class="skeleton skeleton-text" style="width: {90 - i * 10}%;"></div>'
        for i in range(rows)
    )
    st.markdown(f"""
    <div class="skeleton-card">
        <div class="skeleton skeleton-title"></div>
        {skeleton_rows}
    </div>
    """, unsafe_allow_html=True)


def inject_shared_styles():
    """Inject shared CSS into the Streamlit page. Call once at the top."""
    st.markdown(get_shared_css(), unsafe_allow_html=True)

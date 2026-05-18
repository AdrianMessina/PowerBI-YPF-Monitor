"""
YPF BI Monitor - Shared Styles Module
Unified CSS and header components for corporate consistency.
Design system based on UI/UX Pro Max recommendations.
"""
import streamlit as st
from pathlib import Path


# YPF Corporate Color Palette
YPF_BLUE = "#0451E4"
YPF_BLACK = "#000000"
YPF_WHITE = "#FFFFFF"
YPF_GRAY_BG = "#F8FAFC"
YPF_GRAY_TEXT = "#666666"
YPF_TEXT_DARK = "#1E293B"
YPF_BORDER = "#E2E8F0"


def get_shared_css():
    """Return the unified YPF corporate CSS to inject in all apps."""
    return """
    <style>
    /* ==========================================
       YPF BI Monitor - Corporate Design System
       Based on UI/UX Pro Max: Data-Dense Dashboard
       Typography: Fira Sans (body) + Fira Code (code)
       ========================================== */

    /* --- Google Fonts --- */
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Fira+Sans:wght@300;400;500;600;700&display=swap');

    /* --- Base Typography --- */
    html, body, [class*="css"] {
        font-family: 'Fira Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    code, pre, .stCodeBlock, [data-testid="stCode"] {
        font-family: 'Fira Code', 'Consolas', monospace !important;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Fira Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        letter-spacing: -0.01em;
    }

    /* --- Reduced Motion Respect --- */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }
    }

    /* --- App Header Banner --- */
    .ypf-header {
        background: linear-gradient(135deg, #000000 0%, #1a1a2e 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        border-bottom: 4px solid #0451E4;
        margin-bottom: 1.5rem;
    }
    .ypf-header h1 {
        color: #0451E4;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .ypf-header .subtitle {
        color: #cccccc;
        font-size: 0.9rem;
        margin: 0.3rem 0 0 0;
        font-weight: 400;
    }
    .ypf-header .version {
        color: #888888;
        font-size: 0.75rem;
        margin: 0.2rem 0 0 0;
        font-weight: 300;
    }

    /* --- Section Headers --- */
    .section-header {
        background: #E6E6E6;
        border-left: 4px solid #0451E4;
        padding: 0.5rem 1rem;
        font-weight: 600;
        margin: 1rem 0 0.5rem 0;
        border-radius: 0 6px 6px 0;
        font-size: 0.95rem;
    }

    /* --- Info / Help Boxes --- */
    .help-box {
        background: #E6E6E6;
        border-left: 4px solid #0451E4;
        padding: 1rem;
        border-radius: 0 6px 6px 0;
        margin: 0.5rem 0;
    }

    /* --- Buttons (Streamlit) --- */
    .stButton > button {
        background: linear-gradient(135deg, #0451E4 0%, #0340B8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-family: 'Fira Sans', sans-serif !important;
        transition: all 200ms ease-out !important;
        cursor: pointer !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #0340B8 0%, #022A8A 100%) !important;
        box-shadow: 0 4px 12px rgba(4, 81, 228, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: 0 2px 6px rgba(4, 81, 228, 0.2) !important;
    }

    /* --- Download Button --- */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #0451E4 0%, #0340B8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-family: 'Fira Sans', sans-serif !important;
        transition: all 200ms ease-out !important;
        cursor: pointer !important;
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #0340B8 0%, #022A8A 100%) !important;
        box-shadow: 0 4px 12px rgba(4, 81, 228, 0.3) !important;
        transform: translateY(-1px) !important;
    }

    /* --- Expanders --- */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #1E293B;
        cursor: pointer !important;
        transition: color 200ms ease-out;
    }
    .streamlit-expanderHeader:hover {
        color: #0451E4;
    }

    /* --- Metric Cards (Streamlit native) --- */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
        border: 1px solid #E2E8F0;
        border-left: 4px solid #0451E4;
        border-radius: 0 8px 8px 0;
        padding: 1rem 1.25rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        transition: all 200ms ease-out;
    }
    [data-testid="stMetric"]:hover {
        box-shadow: 0 4px 16px rgba(4, 81, 228, 0.1);
        border-left-color: #0340B8;
    }
    [data-testid="stMetricValue"] {
        color: #0451E4 !important;
        font-weight: 700 !important;
        font-family: 'Fira Sans', sans-serif !important;
        font-size: 1.6rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: #1E293B !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.8rem !important;
    }

    /* --- Data Tables --- */
    [data-testid="stDataFrame"] table {
        font-family: 'Fira Sans', sans-serif !important;
    }
    [data-testid="stDataFrame"] th {
        background: #1E293B !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    [data-testid="stDataFrame"] tr:hover td {
        background: rgba(4, 81, 228, 0.04) !important;
    }

    /* --- Tabs --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 2px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Fira Sans', sans-serif !important;
        font-weight: 500;
        color: #666;
        padding: 0.75rem 1.25rem;
        transition: all 200ms ease-out;
        cursor: pointer;
        border-bottom: 3px solid transparent;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #0451E4;
        background: rgba(4, 81, 228, 0.03);
    }
    .stTabs [aria-selected="true"] {
        color: #0451E4 !important;
        font-weight: 600;
        border-bottom: 3px solid #0451E4 !important;
    }

    /* --- Text Inputs --- */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        font-family: 'Fira Sans', sans-serif !important;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        transition: border-color 200ms ease-out, box-shadow 200ms ease-out;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #0451E4 !important;
        box-shadow: 0 0 0 3px rgba(4, 81, 228, 0.1) !important;
    }

    /* --- Selectbox / Dropdown --- */
    .stSelectbox [data-baseweb="select"] {
        font-family: 'Fira Sans', sans-serif !important;
        cursor: pointer;
    }
    .stSelectbox [data-baseweb="select"] > div {
        border-radius: 6px;
        transition: border-color 200ms ease-out;
    }

    /* --- Radio buttons --- */
    .stRadio [data-baseweb="radio"] {
        cursor: pointer !important;
    }

    /* --- Checkboxes --- */
    .stCheckbox {
        cursor: pointer !important;
    }

    /* --- Footer --- */
    .ypf-footer {
        text-align: center;
        color: #666;
        font-size: 0.75rem;
        border-top: 1px solid #E2E8F0;
        padding-top: 0.75rem;
        margin-top: 2rem;
        font-family: 'Fira Sans', sans-serif;
    }

    /* --- Feature Cards (Home page) --- */
    .feature-card {
        background: white;
        border-left: 5px solid #0451E4;
        padding: 1.5rem;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin: 0.5rem 0;
        transition: all 200ms ease-out;
        cursor: default;
    }
    .feature-card:hover {
        box-shadow: 0 4px 16px rgba(4, 81, 228, 0.12);
        border-left-color: #0340B8;
        transform: translateX(2px);
    }
    .feature-card h3 {
        color: #1E293B;
        font-size: 1.05rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
    }
    .feature-card p {
        color: #666;
        font-size: 0.85rem;
        margin: 0;
        line-height: 1.6;
    }
    .feature-card ul {
        color: #666;
        font-size: 0.82rem;
        margin: 0.5rem 0 0 0;
        padding-left: 1.2rem;
        line-height: 1.7;
    }

    /* --- PBIP Input Section --- */
    .pbip-input-section {
        background: rgba(4, 81, 228, 0.03);
        border: 1px solid #E2E8F0;
        border-left: 4px solid #0451E4;
        border-radius: 0 8px 8px 0;
        padding: 1rem;
        margin: 1rem 0;
    }

    /* --- Loader / Spinner (YPF branded) --- */
    .ypf-loader-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 2rem;
    }
    .ypf-loader {
        width: 50px;
        height: 50px;
        border: 4px solid #E2E8F0;
        border-top: 4px solid #0451E4;
        border-radius: 50%;
        animation: ypf-spin 1s linear infinite;
    }
    @keyframes ypf-spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .ypf-loader-text {
        color: #666;
        margin-top: 1rem;
        font-size: 0.9rem;
        font-family: 'Fira Sans', sans-serif;
    }

    /* --- Skeleton Loading Placeholder --- */
    .skeleton {
        background: linear-gradient(90deg, #E2E8F0 25%, #F1F5F9 50%, #E2E8F0 75%);
        background-size: 200% 100%;
        animation: skeleton-pulse 1.5s ease-in-out infinite;
        border-radius: 6px;
        height: 1rem;
        margin: 0.5rem 0;
    }
    .skeleton-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .skeleton-card .skeleton-title {
        height: 1.4rem;
        width: 60%;
        margin-bottom: 1rem;
    }
    .skeleton-card .skeleton-text {
        height: 0.9rem;
        width: 90%;
        margin-bottom: 0.5rem;
    }
    .skeleton-card .skeleton-text:last-child {
        width: 70%;
    }
    @keyframes skeleton-pulse {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }

    /* --- Status Indicators --- */
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 6px;
    }
    .status-dot.active { background: #10B981; }
    .status-dot.warning { background: #F59E0B; }
    .status-dot.error { background: #EF4444; }

    /* --- Dividers --- */
    hr {
        border: none;
        border-top: 1px solid #E2E8F0;
        margin: 1.5rem 0;
    }

    /* --- Scrollbar Styling --- */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #F8FAFC;
    }
    ::-webkit-scrollbar-thumb {
        background: #CBD5E1;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #94A3B8;
    }
    </style>
    """


def render_app_header(title: str, subtitle: str = "", version: str = ""):
    """Render a standardized YPF corporate app header.

    Args:
        title: App title (e.g. "Power BI Analyzer")
        subtitle: Short description
        version: Version string (e.g. "1.1")
    """
    version_html = f'<p class="version">v{version}</p>' if version else ''
    subtitle_html = f'<p class="subtitle">{subtitle}</p>' if subtitle else ''

    st.markdown(f"""
    <div class="ypf-header">
        <h1>{title}</h1>
        {subtitle_html}
        {version_html}
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    """Render a standardized YPF footer."""
    st.markdown("""
    <div class="ypf-footer">
        YPF S.A. &middot; Equipo de desarrollo de visualizacion &middot; 2026
    </div>
    """, unsafe_allow_html=True)


def render_skeleton(rows: int = 3):
    """Render a skeleton loading placeholder.

    Args:
        rows: Number of skeleton text rows to show
    """
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
    """Inject shared CSS into the Streamlit page. Call once at the top of each app."""
    st.markdown(get_shared_css(), unsafe_allow_html=True)

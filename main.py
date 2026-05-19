"""
YPF BI Monitor - Main Entry Point
Suite integrada de herramientas para Power BI
"""

import streamlit as st
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Load .env
_env_path = Path(__file__).parent / '.env'
if _env_path.exists():
    with open(_env_path, 'r') as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _key, _val = _line.split('=', 1)
                os.environ.setdefault(_key.strip(), _val.strip())

from apps import home, powerbi_analyzer, documentation_generator, layout_organizer
from apps import dax_optimizer, usage_dashboard
from shared.usage_logger import UsageLogger

st.set_page_config(
    page_title="YPF BI Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'logger' not in st.session_state:
    st.session_state.logger = UsageLogger(suite_name="YPF_BI_Monitor", version="1.0")
logger = st.session_state.logger

from apps_core.layout_core.shared_styles import inject_shared_styles
inject_shared_styles()

# === CRITICAL CSS: kill dead space + fix sidebar contrast ===
st.markdown("""
<style>
    /* Hide Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
    }
    /* Kill top padding that Streamlit adds */
    .stAppViewBlockContainer,
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 1rem !important;
    }
    .block-container {
        padding-top: 1rem !important;
    }

    /* ---- SIDEBAR ---- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #080E1A 0%, #0F172A 50%, #1E293B 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0.5rem;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #E2E8F0;
    }

    /* Radio nav */
    [data-testid="stSidebar"] .stRadio > label {
        display: none !important;
    }
    [data-testid="stSidebar"] .stRadio > div {
        gap: 2px;
    }
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"] {
        background: transparent;
        cursor: pointer !important;
        border-radius: 6px;
        padding: 0.1rem 0;
        transition: background 120ms ease-out;
        position: relative;
    }
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"]:hover {
        background: rgba(4,81,228,0.15);
    }
    /* NAV TEXT: force white on ALL text inside radio items */
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stRadio label span,
    [data-testid="stSidebar"] .stRadio label p,
    [data-testid="stSidebar"] .stRadio label div,
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"] label,
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"] label *,
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] label,
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] label *,
    [data-testid="stSidebar"] .stRadio p,
    [data-testid="stSidebar"] .stRadio span {
        color: #E2E8F0 !important;
        font-family: 'Fira Sans', sans-serif !important;
        font-size: 0.88rem !important;
    }
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"]:hover label,
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"]:hover label *,
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"]:hover span {
        color: #FFFFFF !important;
    }
    /* Active */
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"][aria-checked="true"] {
        background: rgba(4,81,228,0.18);
    }
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"][aria-checked="true"]::before {
        content: '';
        position: absolute;
        left: 0; top: 15%; bottom: 15%;
        width: 3px;
        background: #0451E4;
        border-radius: 0 2px 2px 0;
    }
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"][aria-checked="true"] label,
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"][aria-checked="true"] label *,
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"][aria-checked="true"] span {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* Sidebar dividers */
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.07);
        margin: 0.6rem 0;
    }

    /* Main headings */
    h1, h2, h3 { color: #0F172A; }
</style>
""", unsafe_allow_html=True)

# ---- SIDEBAR ----
with st.sidebar:
    # Logo + branding compact
    logo_path = Path(__file__).parent / "assets" / "logo_ypf.png"
    if logo_path.exists():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(str(logo_path), width="stretch")

    st.markdown("""
    <div style="text-align: center; padding: 0 0 0.6rem 0;">
        <h2 style="color: #FFFFFF; font-size: 1.25rem; margin: 0; font-weight: 700;
                   font-family: 'Fira Sans', sans-serif; letter-spacing: -0.02em;">
            BI Monitor
        </h2>
        <span style="color: #94A3B8; font-size: 0.65rem;
                     font-family: 'Fira Sans', sans-serif; font-weight: 500;
                     text-transform: uppercase; letter-spacing: 0.1em;">
            Power BI Suite
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio("Nav", [
        "Home",
        "Power BI Analyzer",
        "Documentation Generator",
        "Layout Organizer",
        "DAX Optimizer",
        "Usage Dashboard",
    ], label_visibility="collapsed")

    st.markdown("---")

    # Info + footer compact
    st.markdown("""
    <div style="background: rgba(4,81,228,0.08);
                padding: 0.6rem 0.8rem;
                border-radius: 6px;
                border: 1px solid rgba(4,81,228,0.10);">
        <p style="color: #CBD5E1; margin: 0; font-size: 0.7rem;
                  font-family: 'Fira Sans', sans-serif; line-height: 1.5;">
            Acciones registradas para analisis de uso.
        </p>
    </div>
    <div style="text-align: center; margin-top: 1rem; padding-top: 0.5rem;
                border-top: 1px solid rgba(255,255,255,0.06);">
        <p style="color: #94A3B8; font-size: 0.62rem; margin: 0 0 0.5rem 0;
                  font-family: 'Fira Sans', sans-serif;">
            Para YPF - Gerencia Visualización - DAIA
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Logo DAIA en sidebar
    logo_daia_path = Path(__file__).parent / "assets" / "logo_daia.png"
    if logo_daia_path.exists():
        st.image(str(logo_daia_path), width=180)

# ---- ROUTING ----
try:
    if page == "Home":
        home.render_app(logger)
    elif page == "Power BI Analyzer":
        powerbi_analyzer.render_app(logger)
    elif page == "Documentation Generator":
        documentation_generator.render_app(logger)
    elif page == "Layout Organizer":
        layout_organizer.render_app(logger)
    elif page == "DAX Optimizer":
        dax_optimizer.render_app(logger)
    elif page == "Usage Dashboard":
        usage_dashboard.render_app(logger)
except Exception as e:
    st.error(f"Error al cargar la aplicacion: {str(e)}")
    with st.expander("Ver detalles del error"):
        import traceback
        st.code(traceback.format_exc())

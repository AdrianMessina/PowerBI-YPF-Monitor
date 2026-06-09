"""
YPF BI Monitor - Main Entry Point
Suite integrada de herramientas para Power BI
Design System: Industrial Data Observatory
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env file if exists (for API keys, admin password, etc.)
_env_path = Path(__file__).parent / '.env'
if _env_path.exists():
    with open(_env_path, 'r') as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _key, _val = _line.split('=', 1)
                os.environ.setdefault(_key.strip(), _val.strip())

# Import apps
from apps import home, powerbi_analyzer, documentation_generator, layout_organizer
from apps import dax_optimizer, usage_dashboard

# Import shared logger
from shared.usage_logger import UsageLogger

# Page config
st.set_page_config(
    page_title="YPF BI Monitor",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23F2C811'/><text x='16' y='22' text-anchor='middle' font-size='18' fill='%230B0E14' font-family='monospace'>M</text></svg>",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize logger in session state
if 'logger' not in st.session_state:
    st.session_state.logger = UsageLogger(
        suite_name="YPF_BI_Monitor",
        version="1.0"
    )

logger = st.session_state.logger

# Inject shared Industrial Data Observatory styles
from apps_core.layout_core.shared_styles import inject_shared_styles
inject_shared_styles()

# Sidebar-specific overrides (dark observatory style)
st.markdown("""
<style>
    /* Tighter top padding on main */
    .stAppViewBlockContainer,
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 1rem !important;
    }
    .block-container { padding-top: 1rem !important; }

    /* ── SIDEBAR ─ Industrial Data Observatory ───────────────── */
    [data-testid="stSidebar"] {
        background: var(--surface-1) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.25rem;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: var(--text-primary);
    }

    /* Radio nav items */
    [data-testid="stSidebar"] .stRadio > label {
        display: none !important;
    }
    [data-testid="stSidebar"] .stRadio > div {
        gap: 2px;
    }
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"] {
        background: transparent;
        cursor: pointer !important;
        border-radius: var(--radius-sm);
        padding: 0.15rem 0;
        transition: background var(--duration-normal) var(--ease-out);
        position: relative;
    }
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"]:hover {
        background: var(--brand-accent-muted);
    }

    /* Nav text — force across all variations */
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stRadio label *,
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"] label,
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"] label *,
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] label,
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] label *,
    [data-testid="stSidebar"] .stRadio p,
    [data-testid="stSidebar"] .stRadio span {
        color: var(--text-secondary) !important;
        font-family: var(--font-body) !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"]:hover label,
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"]:hover label *,
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"]:hover span {
        color: var(--text-primary) !important;
    }

    /* Active item — accent slash on left */
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"][aria-checked="true"] {
        background: var(--brand-accent-muted);
    }
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"][aria-checked="true"]::before {
        content: '';
        position: absolute;
        left: 0; top: 12%; bottom: 12%;
        width: 3px;
        background: var(--brand-accent);
        border-radius: 0 2px 2px 0;
    }
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"][aria-checked="true"] label,
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"][aria-checked="true"] label *,
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"][aria-checked="true"] span {
        color: var(--brand-accent) !important;
        font-weight: 600 !important;
    }

    /* Sidebar dividers */
    [data-testid="stSidebar"] hr {
        border: none;
        height: 1px;
        background: var(--border-subtle);
        margin: 0.75rem 0;
        opacity: 0.6;
    }

    /* Sidebar collapse toggle */
    button[data-testid="stSidebarCollapseButton"]:hover {
        color: var(--brand-accent) !important;
    }
    [data-testid="collapsedControl"] {
        background: var(--surface-2) !important;
        border-radius: 0 var(--radius-md) var(--radius-md) 0;
        border: 1px solid var(--border-default);
        border-left: none;
    }
    [data-testid="collapsedControl"] button {
        color: var(--brand-accent) !important;
        background: transparent !important;
    }

    /* Sidebar images — DAIA logo */
    [data-testid="stSidebar"] img {
        opacity: 0.95;
        transition: opacity var(--duration-normal) var(--ease-out);
    }
    [data-testid="stSidebar"] img:hover {
        opacity: 1;
    }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ──────────────────────────────────────────────────────
with st.sidebar:
    # YPF logo — corporate identity anchor at top of sidebar
    logo_ypf_path = Path(__file__).parent / "assets" / "logo_ypf.png"
    if logo_ypf_path.exists():
        col_l, col_c, col_r = st.columns([1, 2, 1])
        with col_c:
            st.image(str(logo_ypf_path), width="stretch")

    # Brand header
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0 0.5rem 0;">
        <h2 style="color: #E8ECF4; font-size: 1.35rem; margin: 0; font-weight: 700;
                   font-family: 'Space Grotesk', sans-serif; letter-spacing: -0.04em;">
            BI <span style="color: #F2C811;">Monitor</span>
        </h2>
        <p style="font-family: 'DM Sans', sans-serif; color: #5A6478; font-size: 0.66rem;
                  margin: 0.4rem 0 0 0; text-transform: uppercase; letter-spacing: 0.12em;
                  font-weight: 500;">
            Power BI Suite
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Navigation
    nav_options = [
        "Home",
        "Power BI Analyzer",
        "Documentation Generator",
        "Layout Organizer",
        "DAX Optimizer",
        "Usage Dashboard",
    ]

    page = st.radio(
        "Nav",
        nav_options,
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Info chip
    st.markdown("""
    <div style="background: rgba(242,200,17,0.06);
                padding: 0.7rem 0.85rem;
                border-radius: 8px;
                border: 1px solid rgba(242,200,17,0.12);
                margin-top: 0.25rem;">
        <p style="color: #8B95A8; margin: 0; font-size: 0.7rem;
                  font-family: 'DM Sans', sans-serif; line-height: 1.55;">
            Acciones registradas para análisis de uso.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Spacer
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Gerencia de Visualización footer
    st.markdown("""
    <div style="text-align: center; padding-top: 0.75rem;
                border-top: 1px solid rgba(255,255,255,0.06);">
        <p style="color: #5A6478; font-size: 0.62rem; margin: 0 0 0.75rem 0;
                  font-family: 'DM Sans', sans-serif; letter-spacing: 0.03em;
                  line-height: 1.5;">
            Para YPF · Gerencia de Visualización · DA&amp;IA
        </p>
    </div>
    """, unsafe_allow_html=True)

    # DA&IA logo
    logo_daia_path = Path(__file__).parent / "assets" / "logo_daia.png"
    if logo_daia_path.exists():
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.image(str(logo_daia_path), width="stretch")

# ── MAIN CONTENT — ROUTING ──────────────────────────────────────
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
    st.error(f"Error al cargar la aplicación: {str(e)}")
    with st.expander("Ver detalles del error"):
        import traceback
        st.code(traceback.format_exc())

    st.info("""
    **Posibles soluciones:**
    - Verifica que todas las dependencias estén instaladas
    - Revisa que los archivos core de cada app estén en su lugar
    - Consulta la documentación de la app específica
    """)

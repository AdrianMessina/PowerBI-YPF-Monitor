"""
Home - Dashboard Principal de YPF BI Monitor
"""

import streamlit as st
from apps_core.layout_core.shared_styles import render_footer


# Emoji Icons (always work, no external dependencies)
_IC = {
    "analyzer": "📊",
    "docgen": "📄",
    "layout": "🗂️",
    "dax": "✨",
}


def _card(icon_key: str, title: str, desc: str, items: list):
    icon = _IC.get(icon_key, '')
    li = ''.join(f'<li>{t}</li>' for t in items)
    st.markdown(f"""
    <div class="feature-card">
        <div class="card-icon">{icon}</div>
        <h3>{title}</h3>
        <p>{desc}</p>
        <ul>{li}</ul>
    </div>
    """, unsafe_allow_html=True)


def render_app(logger):
    """Render home dashboard."""

    # Compact header with stats inline
    st.markdown("""
    <div class="ypf-header" style="padding: 1.25rem 1.75rem; margin-bottom: 1rem;">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem; position: relative; z-index: 1;">
            <div>
                <h1 style="color: #FFF; font-size: 1.35rem; margin: 0; letter-spacing: -0.03em;">YPF BI Monitor</h1>
                <p style="color: #94A3B8; font-size: 0.82rem; margin: 0.15rem 0 0 0;">Suite integrada de herramientas para Power BI</p>
            </div>
            <div style="display: flex; gap: 2rem;">
                <div style="text-align: center;">
                    <div style="font-size: 1.3rem; font-weight: 700; color: #0451E4; letter-spacing: -0.03em;">4</div>
                    <div style="font-size: 0.6rem; font-weight: 500; color: #64748B; text-transform: uppercase; letter-spacing: 0.08em;">Tools</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.3rem; font-weight: 700; color: #0451E4; letter-spacing: -0.03em;">PBIP</div>
                    <div style="font-size: 0.6rem; font-weight: 500; color: #64748B; text-transform: uppercase; letter-spacing: 0.08em;">Formato</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.3rem; font-weight: 700; color: #0451E4; letter-spacing: -0.03em;">DAX</div>
                    <div style="font-size: 0.6rem; font-weight: 500; color: #64748B; text-transform: uppercase; letter-spacing: 0.08em;">Optimizer</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.3rem; font-weight: 700; color: #0451E4; letter-spacing: -0.03em;">DOCX</div>
                    <div style="font-size: 0.6rem; font-weight: 500; color: #64748B; text-transform: uppercase; letter-spacing: 0.08em;">Docs</div>
                </div>
            </div>
        </div>
        <span class="version" style="position: relative; z-index: 1;">v1.0</span>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards - 2x2 compact
    col1, col2 = st.columns(2)

    with col1:
        _card(
            "analyzer",
            "Power BI Analyzer",
            "Analisis de proyectos PBIP con score de calidad, metricas y recomendaciones.",
            ["Tablas, relaciones y medidas DAX", "Score de calidad y recomendaciones", "Export HTML / JSON"]
        )
        _card(
            "docgen",
            "Documentation Generator",
            "Documentacion tecnica-funcional en Word con template corporativo YPF.",
            ["Parseo PBIP/TMDL", "Secciones configurables", "Imagenes y diagramas ER"]
        )

    with col2:
        _card(
            "layout",
            "Layout Organizer",
            "Reorganizacion del diagrama del modelo semantico en layouts optimizados.",
            ["Star schema y Grid layouts", "Deteccion snowflake dimensions", "Tabs por dominio"]
        )
        _card(
            "dax",
            "DAX Optimizer",
            "Analisis estatico de medidas DAX con deteccion de patrones y mejores practicas.",
            ["Deteccion de medidas complejas", "Ranking por criticidad", "Filtrado de comentarios DAX"]
        )

    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        **Como Usar** -- Selecciona una herramienta en el menu lateral,
        indica la ruta del archivo `.pbip` y revisa los resultados.
        """)
    with c2:
        st.markdown("""
        **Soporte** -- Interfaz unificada, logging por usuario,
        identidad corporativa YPF. Contacto: IT Analytics.
        """)

    render_footer()

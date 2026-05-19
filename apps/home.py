"""
Home - Dashboard Principal de YPF BI Monitor
"""

import streamlit as st
from apps_core.layout_core.shared_styles import render_footer


# SVG Icons (Lucide-style)
_IC = {
    "analyzer": '<svg viewBox="0 0 24 24"><path d="M3 3v18h18"/><path d="M7 16l4-8 4 4 4-6"/></svg>',
    "docgen": '<svg viewBox="0 0 24 24"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
    "layout": '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
    "dax": '<svg viewBox="0 0 24 24"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3L12 3Z"/></svg>',
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

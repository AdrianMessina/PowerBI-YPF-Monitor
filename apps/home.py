"""
Home - Dashboard Principal de YPF BI Monitor
"""

import streamlit as st
from pathlib import Path
from apps_core.layout_core.shared_styles import render_app_header, render_footer


def _render_card(title: str, description: str, features: list):
    """Render a feature card using shared CSS class."""
    features_html = ''.join(f'<li>{f}</li>' for f in features)
    st.markdown(f"""
    <div class="feature-card">
        <h3>{title}</h3>
        <p>{description}</p>
        <ul>{features_html}</ul>
    </div>
    """, unsafe_allow_html=True)


def render_app(logger):
    """
    Render home dashboard

    Args:
        logger: Logger de la suite para tracking de uso
    """

    render_app_header(
        "YPF BI Monitor Suite",
        "Suite Integrada de Herramientas para Power BI",
        "1.0"
    )

    st.markdown("""
    ### Bienvenido a YPF BI Monitor

    Esta suite integra **5 herramientas especializadas** para analisis, documentacion y optimizacion
    de reportes Power BI.
    """)

    col1, col2 = st.columns(2)

    with col1:
        _render_card(
            "Power BI Analyzer",
            "Analisis completo de proyectos PBIP con metricas detalladas, visualizaciones interactivas y exportacion.",
            [
                "Analisis de tablas, relaciones y medidas",
                "Evaluacion de paginas y visuales",
                "Recomendaciones de optimizacion"
            ]
        )
        _render_card(
            "Documentation Generator",
            "Generacion automatica de documentacion tecnica-funcional en Word usando template corporativo.",
            [
                "Lectura de archivos PBIP",
                "Formularios con campos autocompletables",
                "Soporte para imagenes y diagramas ER"
            ]
        )
        _render_card(
            "Layout Organizer",
            "Organizacion automatica de diagramas de modelo Power BI en layouts limpios y optimizados.",
            [
                "Star y Grid layouts",
                "Deteccion de snowflake dimensions",
                "Creacion de tabs focalizados"
            ]
        )

    with col2:
        _render_card(
            "DAX Optimizer",
            "Analisis y optimizacion de medidas DAX con recomendaciones de rendimiento y mejores practicas.",
            [
                "Deteccion de medidas complejas",
                "Ranking de optimizacion",
                "Visualizaciones de analisis"
            ]
        )
        _render_card(
            "BI Bot",
            "Asistente conversacional para analisis de reportes Power BI mediante consultas en lenguaje natural.",
            [
                "Lectura de archivos PBIP",
                "Respuestas contextuales",
                "Analisis de estructura de datos"
            ]
        )
        _render_card(
            "Usage Dashboard",
            "Dashboard de metricas y estadisticas de uso de todas las herramientas de la suite (solo admins).",
            [
                "Tracking de eventos por usuario",
                "Metricas de uso por app",
                "Analisis temporal"
            ]
        )

    st.markdown("---")

    # How to use - compact
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### Como Usar
        1. **Selecciona una herramienta** en el menu lateral izquierdo
        2. **Sigue las instrucciones** especificas de cada aplicacion
        3. **Todas las acciones quedan registradas** para analisis de uso
        """)
    with col2:
        st.markdown("""
        ### Caracteristicas
        - **Interfaz Unificada** -- Navegacion consistente entre apps
        - **Logging Centralizado** -- Tracking automatico por usuario
        - **Diseno Corporativo** -- Colores y estilos YPF
        - **Soporte** -- Contacta al equipo de IT Analytics
        """)

    st.markdown("---")
    render_footer()

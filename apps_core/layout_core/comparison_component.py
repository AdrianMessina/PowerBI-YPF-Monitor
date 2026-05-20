"""
Comparison Component - Before/After Layout Visualization
Elegant before/after comparison for Power BI model layouts
"""
import streamlit as st
from pathlib import Path


def render_layout_comparison():
    """
    Renders an elegant before/after comparison of Power BI model layouts.
    Uses YPF corporate design system with refined aesthetics.
    """
    # Paths to comparison images
    before_img = Path(__file__).parent.parent.parent / "assets" / "diagram_before.jpg"
    after_img = Path(__file__).parent.parent.parent / "assets" / "diagram_after.jpg"

    # Inject custom CSS for refined comparison component
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Sans:wght@300;400;500;600;700&display=swap');

    .comparison-section {
        font-family: 'Fira Sans', sans-serif;
        margin: 2.5rem 0;
        padding: 0;
    }

    .comparison-header {
        text-align: center;
        margin-bottom: 2rem;
    }

    .comparison-header h3 {
        font-size: 1.5rem;
        font-weight: 600;
        color: #0F172A;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.02em;
    }

    .comparison-header p {
        font-size: 0.95rem;
        color: #64748B;
        margin: 0;
        font-weight: 400;
    }

    .comparison-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
        margin: 0 auto;
        max-width: 1400px;
    }

    .comparison-card {
        position: relative;
        background: #FFFFFF;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #E2E8F0;
        transition: all 320ms cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }

    .comparison-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(4,81,228,0.12);
        border-color: rgba(4,81,228,0.2);
    }

    .comparison-badge {
        position: absolute;
        top: 1rem;
        left: 1rem;
        padding: 0.4rem 1rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        z-index: 10;
        backdrop-filter: blur(12px);
    }

    .badge-before {
        background: rgba(239, 68, 68, 0.92);
        color: #FFFFFF;
        box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
    }

    .badge-after {
        background: rgba(5, 150, 105, 0.92);
        color: #FFFFFF;
        box-shadow: 0 2px 8px rgba(5, 150, 105, 0.3);
    }

    .comparison-image-wrapper {
        position: relative;
        width: 100%;
        aspect-ratio: 16/9;
        overflow: hidden;
        background: #F8FAFC;
    }

    .comparison-image-wrapper img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 420ms cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }

    .comparison-card:hover .comparison-image-wrapper img {
        transform: scale(1.05);
    }

    .comparison-caption {
        padding: 1.25rem 1.5rem;
        background: linear-gradient(to bottom, #FFFFFF 0%, #F8FAFC 100%);
    }

    .comparison-caption h4 {
        font-size: 1.05rem;
        font-weight: 600;
        color: #1E293B;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.015em;
    }

    .comparison-caption p {
        font-size: 0.85rem;
        color: #64748B;
        line-height: 1.6;
        margin: 0;
    }

    .comparison-icon {
        display: inline-block;
        margin-right: 0.5rem;
        font-size: 1.1rem;
        vertical-align: middle;
    }

    .improvement-metrics {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #E2E8F0;
    }

    .metric {
        flex: 1;
        text-align: center;
    }

    .metric-value {
        font-size: 1.3rem;
        font-weight: 700;
        color: #0451E4;
        display: block;
        letter-spacing: -0.02em;
    }

    .metric-label {
        font-size: 0.7rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.25rem;
    }

    @media (max-width: 1024px) {
        .comparison-container {
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }
    }

    /* Fade-in animation */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .comparison-card {
        animation: fadeInUp 600ms cubic-bezier(0.25, 0.46, 0.45, 0.94) backwards;
    }

    .comparison-card:nth-child(1) {
        animation-delay: 100ms;
    }

    .comparison-card:nth-child(2) {
        animation-delay: 200ms;
    }
    </style>
    """, unsafe_allow_html=True)

    # Render comparison component
    st.markdown("""
    <div class="comparison-section">
        <div class="comparison-header">
            <h3>✨ Transformación Visual del Modelo</h3>
            <p>Antes y después de aplicar el layout automático</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Create two-column layout
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="comparison-card">
            <span class="comparison-badge badge-before">Antes</span>
        """, unsafe_allow_html=True)

        if before_img.exists():
            st.image(str(before_img), use_container_width=True)

        st.markdown("""
            <div class="comparison-caption">
                <h4><span class="comparison-icon">❌</span>Modelo Desordenado</h4>
                <p>
                    Tablas superpuestas, relaciones cruzadas y difícil navegación.
                    El modelo es complejo de entender y mantener.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="comparison-card">
            <span class="comparison-badge badge-after">Después</span>
        """, unsafe_allow_html=True)

        if after_img.exists():
            st.image(str(after_img), use_container_width=True)

        st.markdown("""
            <div class="comparison-caption">
                <h4><span class="comparison-icon">✅</span>Modelo Optimizado</h4>
                <p>
                    Esquema estrella perfectamente organizado. Hechos arriba,
                    dimensiones alineadas. Claridad instantánea.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Improvement metrics
    st.markdown("""
    <div style="max-width: 800px; margin: 2rem auto;">
        <div class="improvement-metrics">
            <div class="metric">
                <span class="metric-value">+85%</span>
                <div class="metric-label">Legibilidad</div>
            </div>
            <div class="metric">
                <span class="metric-value">-90%</span>
                <div class="metric-label">Cruces</div>
            </div>
            <div class="metric">
                <span class="metric-value">100%</span>
                <div class="metric-label">Automático</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

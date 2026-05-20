"""
Documentation Generator Showcase - What gets documented automatically
Compact intro showcase that appears below the app header
"""
import streamlit as st


def render_docgen_showcase():
    """
    Renders a concise intro showcase explaining what the documentation generator documents.
    Positioned right after the app header, matching the style of other apps.
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Sans:wght@300;400;500;600;700&display=swap');

    .docgen-intro {
        font-family: 'Fira Sans', sans-serif;
        background: linear-gradient(135deg, rgba(4,81,228,0.08) 0%, rgba(4,81,228,0.02) 100%);
        border-left: 4px solid #0451E4;
        border-radius: 0 12px 12px 0;
        padding: 1.5rem 2rem;
        margin: 1.5rem 0;
    }

    .docgen-intro h3 {
        font-size: 1.3rem;
        font-weight: 600;
        color: #0F172A;
        margin: 0 0 0.75rem 0;
        letter-spacing: -0.02em;
    }

    .docgen-intro p {
        font-size: 0.95rem;
        color: #475569;
        line-height: 1.6;
        margin: 0 0 1.25rem 0;
    }

    .capabilities-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 0.75rem;
        margin: 0;
    }

    .capability-item {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        transition: all 240ms ease;
    }

    .capability-item:hover {
        border-color: rgba(4,81,228,0.3);
        box-shadow: 0 4px 12px rgba(4,81,228,0.08);
        transform: translateY(-2px);
    }

    .capability-icon {
        display: inline-block;
        font-size: 1.2rem;
        margin-right: 0.6rem;
        vertical-align: middle;
    }

    .capability-text {
        display: inline-block;
        font-size: 0.88rem;
        font-weight: 500;
        color: #1E293B;
        vertical-align: middle;
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .capability-item {
        animation: fadeInUp 400ms ease backwards;
    }

    .capability-item:nth-child(1) { animation-delay: 50ms; }
    .capability-item:nth-child(2) { animation-delay: 100ms; }
    .capability-item:nth-child(3) { animation-delay: 150ms; }
    .capability-item:nth-child(4) { animation-delay: 200ms; }
    .capability-item:nth-child(5) { animation-delay: 250ms; }
    .capability-item:nth-child(6) { animation-delay: 300ms; }
    </style>

    <div class="docgen-intro">
        <h3>📚 ¿Qué documenta automáticamente?</h3>
        <p>
            Analiza tu proyecto Power BI y genera documentación técnica-funcional completa en formato Word:
        </p>
        <div class="capabilities-grid">
            <div class="capability-item">
                <span class="capability-icon">🗂️</span>
                <span class="capability-text">Tablas del modelo</span>
            </div>
            <div class="capability-item">
                <span class="capability-icon">📊</span>
                <span class="capability-text">Medidas DAX</span>
            </div>
            <div class="capability-item">
                <span class="capability-icon">🔗</span>
                <span class="capability-text">Relaciones</span>
            </div>
            <div class="capability-item">
                <span class="capability-icon">📐</span>
                <span class="capability-text">Columnas calculadas</span>
            </div>
            <div class="capability-item">
                <span class="capability-icon">📈</span>
                <span class="capability-text">Visualizaciones</span>
            </div>
            <div class="capability-item">
                <span class="capability-icon">🎨</span>
                <span class="capability-text">Diagrama ER</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

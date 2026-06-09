"""
Usage Dashboard - Metricas de Uso de YPF BI Monitor
Herramienta interna con acceso restringido (solo administradores)
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

from apps_core.layout_core.shared_styles import render_app_header, render_footer
from shared.auth import Authenticator


def render_app(logger):
    """
    Render usage dashboard (admin only)

    Args:
        logger: Logger de la suite para tracking de uso
    """
    # Table layout fine-tuning (color comes from shared Industrial Data Observatory styles)
    st.markdown("""
    <style>
    .stDataFrame {
        width: 100% !important;
        overflow-x: auto !important;
    }
    .stDataFrame table {
        width: 100% !important;
        table-layout: auto !important;
    }
    .stDataFrame td, .stDataFrame th {
        white-space: nowrap !important;
        padding: 0.7rem 1rem !important;
        font-size: 0.85rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

    render_app_header(
        "Usage Dashboard",
        "Metricas y estadisticas de uso de YPF BI Monitor",
        "1.0"
    )

    # Require admin authentication
    auth = Authenticator()
    if not auth.require_auth(admin_only=False):
        render_footer()
        return

    # Show logged-in user and logout option
    auth.render_user_info()

    # Get events from logger backend
    all_events = logger.get_all_events()

    if not all_events:
        st.warning("No hay datos de uso disponibles todavia.")
        st.info("Usa las aplicaciones y luego regresa aqui para ver las estadisticas.")
        render_footer()
        return

    # Convert to DataFrame
    df = pd.DataFrame(all_events)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date

    # Ensure username/hostname columns exist and fill NaN (backward compat with old logs)
    if 'username' not in df.columns:
        df['username'] = 'unknown'
    else:
        df['username'] = df['username'].fillna('unknown').astype(str)
    if 'hostname' not in df.columns:
        df['hostname'] = 'unknown'
    else:
        df['hostname'] = df['hostname'].fillna('unknown').astype(str)

    # Main metrics
    st.markdown("### Resumen General")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        total_events = len(df)
        st.metric("Total Eventos", f"{total_events:,}")

    with col2:
        unique_sessions = df['session_id'].nunique()
        st.metric("Sesiones Unicas", f"{unique_sessions:,}")

    with col3:
        unique_users = df['username'].nunique()
        st.metric("Usuarios Unicos", f"{unique_users:,}")

    with col4:
        date_range = (df['timestamp'].max() - df['timestamp'].min()).days + 1
        st.metric("Dias con Datos", f"{date_range}")

    with col5:
        events_per_day = total_events / date_range if date_range > 0 else 0
        st.metric("Eventos/Dia (Prom)", f"{events_per_day:.1f}")

    st.markdown("---")

    # Events by type
    st.markdown("### Eventos por Tipo")

    event_counts = df['event'].value_counts().reset_index()
    event_counts.columns = ['Evento', 'Cantidad']

    col1, col2 = st.columns([1, 2])

    with col1:
        st.dataframe(event_counts, use_container_width=True, hide_index=True)

    with col2:
        fig = px.bar(event_counts, x='Cantidad', y='Evento',
                     orientation='h',
                     title='Distribucion de Eventos',
                     color='Cantidad',
                     color_continuous_scale=['#E6E6E6', '#0451E4'])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Events by day
    st.markdown("### Actividad Temporal")

    daily_events = df.groupby('date').size().reset_index(name='eventos')
    daily_events['date'] = pd.to_datetime(daily_events['date'])

    fig = px.line(daily_events, x='date', y='eventos',
                  title='Eventos por Dia',
                  markers=True)
    fig.update_traces(line_color='#0451E4')
    fig.update_xaxes(title='Fecha')
    fig.update_yaxes(title='Numero de Eventos')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Per-user analysis
    st.markdown("### Actividad por Usuario")

    # User filter
    all_users = sorted(df['username'].unique().tolist())
    selected_user = st.selectbox(
        "Filtrar por usuario (dejar 'Todos' para ver todos)",
        options=['Todos'] + all_users,
        key="user_filter"
    )

    if selected_user != 'Todos':
        df_filtered = df[df['username'] == selected_user]
    else:
        df_filtered = df

    # Enhanced user summary table with per-app metrics
    user_stats = df.groupby('username').agg(
        sesiones=('session_id', 'nunique'),
        eventos=('event', 'count'),
        primera_vez=('timestamp', 'min'),
        ultima_vez=('timestamp', 'max')
    ).reset_index()

    # Add app-specific metrics
    def detect_app(event_name):
        if 'pbi_analysis' in event_name or 'powerbi_analyzer' in event_name:
            return 'Analyzer'
        elif 'docgen' in event_name:
            return 'DocGen'
        elif 'layout' in event_name:
            return 'Layout'
        elif 'dax' in event_name:
            return 'DAX'
        elif 'bot' in event_name or 'bi_bot' in event_name:
            return 'Bot'
        else:
            return None

    df['app'] = df['event'].apply(detect_app)

    # Count events per user per app
    app_usage_per_user = df[df['app'].notna()].groupby(['username', 'app']).size().unstack(fill_value=0)

    # Merge with user_stats
    user_stats = user_stats.merge(app_usage_per_user, left_on='username', right_index=True, how='left')

    # Fill NaN with 0 for apps not used
    for col in ['Analyzer', 'DocGen', 'Layout', 'DAX', 'Bot']:
        if col not in user_stats.columns:
            user_stats[col] = 0
        else:
            user_stats[col] = user_stats[col].fillna(0).astype(int)

    user_stats['primera_vez'] = user_stats['primera_vez'].dt.strftime('%Y-%m-%d %H:%M')
    user_stats['ultima_vez'] = user_stats['ultima_vez'].dt.strftime('%Y-%m-%d %H:%M')

    # Reorder columns
    base_cols = ['username', 'sesiones', 'eventos', 'primera_vez', 'ultima_vez']
    app_cols = [col for col in ['Analyzer', 'DocGen', 'Layout', 'DAX', 'Bot'] if col in user_stats.columns]
    user_stats = user_stats[base_cols + app_cols]

    user_stats.columns = ['Usuario', 'Sesiones', 'Eventos Total', 'Primera Actividad', 'Ultima Actividad'] + app_cols
    user_stats = user_stats.sort_values('Eventos Total', ascending=False)

    # Display table (full width for better space usage)
    st.dataframe(user_stats, use_container_width=True, hide_index=True, height=400)

    # Chart below
    st.markdown("#### Visualización de Eventos por Usuario")
    fig = px.bar(user_stats, x='Usuario', y='Eventos Total',
                 title='Eventos Totales por Usuario',
                 color='Sesiones',
                 color_continuous_scale=['#E6E6E6', '#0451E4'])
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    # Per-user daily activity (if a specific user is selected)
    if selected_user != 'Todos':
        st.markdown(f"#### Actividad diaria de {selected_user}")
        user_daily = df_filtered.groupby('date').size().reset_index(name='eventos')
        user_daily['date'] = pd.to_datetime(user_daily['date'])
        fig = px.bar(user_daily, x='date', y='eventos',
                     title=f'Eventos por Dia - {selected_user}')
        fig.update_traces(marker_color='#0451E4')
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Analysis by app
    st.markdown("### Analisis por App")

    def detect_app(event_name):
        if 'pbi_analysis' in event_name or 'powerbi_analyzer' in event_name:
            return 'Power BI Analyzer'
        elif 'docgen' in event_name:
            return 'Documentation Generator'
        elif 'layout' in event_name:
            return 'Layout Organizer'
        elif 'dax' in event_name:
            return 'DAX Optimizer'
        elif 'bot' in event_name or 'bi_bot' in event_name:
            return 'BI Bot'
        elif 'session' in event_name:
            return 'Sistema'
        else:
            return 'Otro'

    df['app'] = df['event'].apply(detect_app)
    df_filtered['app'] = df_filtered['event'].apply(detect_app)

    app_usage = df_filtered[df_filtered['app'] != 'Sistema'].groupby('app').size().reset_index(name='eventos')
    app_usage = app_usage.sort_values('eventos', ascending=False)

    if not app_usage.empty:
        col1, col2 = st.columns([1, 2])

        with col1:
            st.dataframe(app_usage, use_container_width=True, hide_index=True)

        with col2:
            fig = px.pie(app_usage, values='eventos', names='app',
                         title='Uso por Aplicación',
                         color_discrete_sequence=['#F2C811', '#0078D4', '#8B5CF6', '#10B981', '#EC4899', '#F59E0B'])
            fig.update_traces(textfont={'family': 'JetBrains Mono', 'color': '#0B0E14'})
            fig.update_layout(
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': '#E8ECF4', 'family': 'DM Sans, sans-serif'},
                title_font={'family': 'Space Grotesk, sans-serif', 'size': 14, 'color': '#E8ECF4'},
                legend={'font': {'color': '#8B95A8'}}
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aun no hay suficientes datos para analisis por app")

    st.markdown("---")

    # Recent events (respects user filter)
    st.markdown("### Ultimos Eventos")

    recent_events = df_filtered.sort_values('timestamp', ascending=False).head(100)
    display_df = recent_events[['timestamp', 'username', 'hostname', 'event', 'session_id']].copy()
    display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    display_df.columns = ['Fecha/Hora', 'Usuario', 'Equipo', 'Evento', 'Session ID']

    st.dataframe(display_df, use_container_width=True, hide_index=True, height=500)

    # Export
    st.markdown("---")
    st.markdown("### Exportar Datos")

    csv = df.to_csv(index=False)
    st.download_button(
        label="Descargar CSV completo",
        data=csv,
        file_name=f"ypf_bi_monitor_usage_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

    # ── Methodology block ───────────────────────────────────────────
    st.markdown("---")
    _render_score_methodology()

    render_footer()


def _render_score_methodology():
    """Render a discreet, corporate-aligned methodology section for the score.

    Explains the 4 quality dimensions used by Power BI Analyzer to compute the
    overall score, with weights and thresholds, in Industrial Data Observatory style.
    """
    st.markdown("""
    <div style="display:flex; align-items:baseline; justify-content:space-between; margin-bottom:0.6rem;">
        <h3 style="font-family:'Space Grotesk',sans-serif; color:#E8ECF4; margin:0;
                   font-weight:700; letter-spacing:-0.03em; font-size:1.05rem;">
            Metodología del Score
        </h3>
        <span style="font-family:'JetBrains Mono',monospace; color:#5A6478;
                     font-size:0.6rem; letter-spacing:0.16em; text-transform:uppercase;">
            v2.0 · 4 dimensiones
        </span>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("¿Cómo se construye la métrica de calidad?", expanded=False):
        st.markdown("""
        <p style="color:#8B95A8; font-size:0.86rem; line-height:1.6; margin:0 0 1rem 0;">
            El score global del Power BI Analyzer se calcula como un
            <strong style="color:#E8ECF4;">promedio ponderado de 4 dimensiones de calidad</strong>,
            cada una alimentada por métricas específicas medidas sobre el reporte.
            Las dimensiones reflejan los pilares de un reporte sostenible.
        </p>
        """, unsafe_allow_html=True)

        dims = [
            {
                'label': 'Modelo Semántico',
                'weight': '35%',
                'desc': 'Cimiento del reporte. Mide la calidad estructural del diseño de datos.',
                'metrics': ['Cantidad de tablas', 'Relaciones totales', 'Relaciones bidireccionales',
                            'Columnas calculadas', 'Tamaño del modelo'],
            },
            {
                'label': 'DAX / Performance',
                'weight': '25%',
                'desc': 'Calidad de medidas DAX y su impacto en el rendimiento del reporte.',
                'metrics': ['Medidas DAX complejas'],
            },
            {
                'label': 'Diseño del Reporte',
                'weight': '25%',
                'desc': 'Composición visual: densidad por página, filtros y assets embebidos.',
                'metrics': ['Visualizaciones por página', 'Filtros por página', 'Imágenes embebidas (MB)'],
            },
            {
                'label': 'Gobernanza / Mantenibilidad',
                'weight': '15%',
                'desc': 'Buenas prácticas y mantenibilidad a largo plazo.',
                'metrics': ['Custom visuals', 'Total de páginas'],
            },
        ]

        cols = st.columns(4)
        for col, dim in zip(cols, dims):
            metrics_html = ''.join(
                f'<li style="color:#8B95A8; font-size:0.76rem; line-height:1.55; '
                f'margin-bottom:0.15rem;">{m}</li>'
                for m in dim['metrics']
            )
            with col:
                st.markdown(f"""
                <div style="background:#181D2A; border:1px solid #1A2030;
                            border-left:3px solid #F2C811; border-radius:10px;
                            padding:1rem 1.1rem; height:100%;">
                    <div style="display:inline-block; font-family:'JetBrains Mono',monospace;
                                color:#F2C811; font-size:0.62rem; letter-spacing:0.14em;
                                font-weight:600; padding:0.15rem 0.5rem; border-radius:4px;
                                background:rgba(242,200,17,0.10);
                                border:1px solid rgba(242,200,17,0.20); margin-bottom:0.6rem;">
                        {dim['weight']}
                    </div>
                    <div style="font-family:'Space Grotesk',sans-serif; color:#E8ECF4;
                                font-size:0.88rem; font-weight:600; letter-spacing:-0.01em;
                                line-height:1.25; margin-bottom:0.4rem;">
                        {dim['label']}
                    </div>
                    <p style="color:#8B95A8; font-size:0.74rem; line-height:1.55;
                              margin:0 0 0.65rem 0;">
                        {dim['desc']}
                    </p>
                    <div style="font-family:'JetBrains Mono',monospace; color:#5A6478;
                                font-size:0.58rem; letter-spacing:0.12em; text-transform:uppercase;
                                margin-bottom:0.35rem;">
                        Métricas
                    </div>
                    <ul style="margin:0; padding-left:0.95rem;">{metrics_html}</ul>
                </div>
                """, unsafe_allow_html=True)

        # Thresholds block
        st.markdown("""
        <div style="margin-top:1.25rem; background:#181D2A; border:1px solid #1A2030;
                    border-radius:10px; padding:1rem 1.25rem;">
            <div style="font-family:'JetBrains Mono',monospace; color:#5A6478;
                        font-size:0.6rem; letter-spacing:0.14em; text-transform:uppercase;
                        margin-bottom:0.65rem;">
                Umbrales de Score Global
            </div>
            <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:0.75rem;">
                <div style="text-align:center;">
                    <div style="font-family:'JetBrains Mono',monospace; color:#10B981;
                                font-size:1.1rem; font-weight:600;">90 – 100</div>
                    <div style="color:#8B95A8; font-size:0.72rem; margin-top:0.15rem;">Excelente</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-family:'JetBrains Mono',monospace; color:#0078D4;
                                font-size:1.1rem; font-weight:600;">75 – 89</div>
                    <div style="color:#8B95A8; font-size:0.72rem; margin-top:0.15rem;">Bueno</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-family:'JetBrains Mono',monospace; color:#F59E0B;
                                font-size:1.1rem; font-weight:600;">60 – 74</div>
                    <div style="color:#8B95A8; font-size:0.72rem; margin-top:0.15rem;">Atención</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-family:'JetBrains Mono',monospace; color:#D13438;
                                font-size:1.1rem; font-weight:600;">0 – 59</div>
                    <div style="color:#8B95A8; font-size:0.72rem; margin-top:0.15rem;">Crítico</div>
                </div>
            </div>
            <p style="color:#5A6478; font-size:0.7rem; line-height:1.55;
                      margin:0.85rem 0 0 0; text-align:center;">
                Umbrales alineados con el sistema del Power BI Fixer para mantener consistencia
                entre las herramientas de la suite.
            </p>
        </div>
        """, unsafe_allow_html=True)

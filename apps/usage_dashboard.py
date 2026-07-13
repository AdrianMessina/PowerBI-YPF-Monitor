"""
Usage Dashboard - Metricas de Uso de YPF BI Monitor
Herramienta interna con acceso restringido
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

from apps_core.layout_core.shared_styles import render_app_header, render_footer
from shared.auth import Authenticator


def detect_app(event_name):
    """Map event name to app name"""
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


def extract_data_field(data, field):
    """Safely extract a field from event data dict"""
    if isinstance(data, dict):
        return data.get(field)
    return None


def render_app(logger):
    """
    Render usage dashboard

    Args:
        logger: Logger de la suite para tracking de uso
    """
    # CSS for improved layout
    st.markdown("""
    <style>
    .stDataFrame {
        width: 100% !important;
    }
    .stDataFrame table {
        width: 100% !important;
        table-layout: auto !important;
    }
    .stDataFrame td, .stDataFrame th {
        white-space: nowrap !important;
        padding: 0.6rem 1rem !important;
        font-size: 0.88rem !important;
    }
    .stDataFrame th {
        background: linear-gradient(135deg, #0451E4 0%, #033fa8 100%) !important;
        color: white !important;
        font-weight: 600 !important;
    }
    .dashboard-warning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.04) 100%);
        border-left: 4px solid #F59E0B;
        padding: 1rem 1.5rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        font-size: 0.92rem;
        color: #78350F;
    }
    .filter-section {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    render_app_header(
        "Usage Dashboard",
        "Metricas y comparativa antes/despues de YPF BI Monitor",
        "1.1"
    )

    # Require authentication
#     auth = Authenticator()
#     if not auth.require_auth(admin_only=False):
#         render_footer()
#         return
# 
#     auth.render_user_info()

    # Warning about file naming
    st.markdown("""
    <div class="dashboard-warning">
        ⚠️ <strong>Importante:</strong> No cambies el nombre de tus archivos .pbip entre analisis.
        Las comparativas antes/despues se basan en el nombre del archivo. Si cambias el nombre,
        el sistema lo tratara como un reporte diferente y no podras ver la evolucion de tus mejoras.
    </div>
    """, unsafe_allow_html=True)

    # Get events
    all_events = logger.get_all_events()

    if not all_events:
        st.warning("No hay datos de uso disponibles todavia.")
        st.info("Usa las aplicaciones y luego regresa aqui para ver las estadisticas.")
        render_footer()
        return

    # Build DataFrame
    df = pd.DataFrame(all_events)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date

    # Ensure columns
    if 'username' not in df.columns:
        df['username'] = 'unknown'
    else:
        df['username'] = df['username'].fillna('unknown').astype(str)
    if 'hostname' not in df.columns:
        df['hostname'] = 'unknown'
    else:
        df['hostname'] = df['hostname'].fillna('unknown').astype(str)

    # Add app classification
    df['app'] = df['event'].apply(detect_app)

    # Extract score and filename from data field
    df['score'] = df['data'].apply(lambda x: extract_data_field(x, 'score'))
    df['filename'] = df['data'].apply(lambda x: extract_data_field(x, 'filename') or extract_data_field(x, 'pbip_file'))

    # ============================================================
    # FILTERS SECTION
    # ============================================================
    st.markdown("### 🔍 Filtros")

    with st.container():
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            all_users = sorted(df['username'].unique().tolist())
            selected_user = st.selectbox(
                "Usuario",
                options=['Todos'] + all_users,
                key="filter_user"
            )

        with col2:
            all_apps = sorted([a for a in df['app'].unique().tolist() if a != 'Sistema'])
            selected_app = st.selectbox(
                "Aplicacion",
                options=['Todas'] + all_apps,
                key="filter_app"
            )

        with col3:
            min_date = df['timestamp'].min().date()
            max_date = df['timestamp'].max().date()
            date_from = st.date_input(
                "Desde",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key="filter_date_from"
            )

        with col4:
            date_to = st.date_input(
                "Hasta",
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                key="filter_date_to"
            )

    # Apply filters
    df_filtered = df.copy()
    if selected_user != 'Todos':
        df_filtered = df_filtered[df_filtered['username'] == selected_user]
    if selected_app != 'Todas':
        df_filtered = df_filtered[df_filtered['app'] == selected_app]
    df_filtered = df_filtered[
        (df_filtered['date'] >= date_from) &
        (df_filtered['date'] <= date_to)
    ]

    st.markdown("---")

    # ============================================================
    # GENERAL METRICS
    # ============================================================
    st.markdown("### 📊 Resumen General")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Eventos", f"{len(df_filtered):,}")
    with col2:
        st.metric("Sesiones", f"{df_filtered['session_id'].nunique():,}")
    with col3:
        st.metric("Usuarios", f"{df_filtered['username'].nunique():,}")
    with col4:
        analyses_count = len(df_filtered[df_filtered['score'].notna()])
        st.metric("Analisis con Score", f"{analyses_count:,}")
    with col5:
        avg_score = df_filtered['score'].mean()
        st.metric("Score Promedio", f"{avg_score:.1f}" if pd.notna(avg_score) else "N/A")

    st.markdown("---")

    # ============================================================
    # ANALYSIS WITH SCORES (Before/After comparison)
    # ============================================================
    st.markdown("### 🎯 Analisis con Metricas (Comparativa Antes/Despues)")

    analyses_df = df_filtered[df_filtered['score'].notna()].copy()

    if not analyses_df.empty:
        # Build comparison table per file
        analyses_df['Fecha'] = analyses_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
        analyses_df = analyses_df.sort_values('timestamp')

        # Add iteration number per file
        analyses_df['Iteracion'] = analyses_df.groupby(['username', 'filename']).cumcount() + 1

        # Display table
        display_cols = ['Fecha', 'username', 'app', 'filename', 'Iteracion', 'score']
        display_df = analyses_df[display_cols].copy()
        display_df.columns = ['Fecha', 'Usuario', 'App', 'Archivo', 'Iteracion', 'Score']
        display_df = display_df.sort_values('Fecha', ascending=False)

        st.dataframe(display_df, use_container_width=True, hide_index=True, height=350)

        # Before/After chart - evolution per file
        files_with_multiple = analyses_df.groupby(['username', 'filename']).size()
        files_with_multiple = files_with_multiple[files_with_multiple >= 2].reset_index()

        if not files_with_multiple.empty:
            st.markdown("#### 📈 Evolucion del Score por Archivo")
            st.caption("Solo se muestran archivos analizados al menos 2 veces")

            evolution_df = analyses_df.merge(
                files_with_multiple[['username', 'filename']],
                on=['username', 'filename'],
                how='inner'
            )
            evolution_df['etiqueta'] = evolution_df['username'] + ' - ' + evolution_df['filename'].fillna('sin_nombre')

            fig = px.line(
                evolution_df,
                x='timestamp',
                y='score',
                color='etiqueta',
                markers=True,
                title='Evolucion del Score - Antes vs Despues',
                labels={'timestamp': 'Fecha', 'score': 'Score', 'etiqueta': 'Usuario - Archivo'}
            )
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)

            # Show improvement summary
            st.markdown("#### 🚀 Resumen de Mejoras")
            improvements = []
            for (user, fname), group in evolution_df.groupby(['username', 'filename']):
                group_sorted = group.sort_values('timestamp')
                first_score = group_sorted.iloc[0]['score']
                last_score = group_sorted.iloc[-1]['score']
                delta = last_score - first_score
                improvements.append({
                    'Usuario': user,
                    'Archivo': fname,
                    'Score Inicial': first_score,
                    'Score Actual': last_score,
                    'Mejora': delta,
                    'Iteraciones': len(group_sorted)
                })

            improvements_df = pd.DataFrame(improvements)
            improvements_df = improvements_df.sort_values('Mejora', ascending=False)
            st.dataframe(improvements_df, use_container_width=True, hide_index=True)
        else:
            st.info("💡 Realiza al menos 2 analisis del mismo archivo para ver la comparativa antes/despues")
    else:
        st.info("Aun no hay analisis con metricas registradas. Usa Power BI Analyzer para empezar.")

    st.markdown("---")

    # ============================================================
    # USER ACTIVITY
    # ============================================================
    st.markdown("### 👥 Actividad por Usuario")

    user_stats = df_filtered.groupby('username').agg(
        sesiones=('session_id', 'nunique'),
        eventos=('event', 'count'),
        primera_vez=('timestamp', 'min'),
        ultima_vez=('timestamp', 'max')
    ).reset_index()

    # Count events per user per app
    df_with_app = df_filtered[df_filtered['app'].isin(
        ['Power BI Analyzer', 'Documentation Generator', 'Layout Organizer', 'DAX Optimizer', 'BI Bot']
    )]

    if not df_with_app.empty:
        app_usage_per_user = df_with_app.groupby(['username', 'app']).size().unstack(fill_value=0)
        user_stats = user_stats.merge(app_usage_per_user, left_on='username', right_index=True, how='left')

    # Fill NaN with 0 for apps not used
    app_short_names = {
        'Power BI Analyzer': 'Analyzer',
        'Documentation Generator': 'DocGen',
        'Layout Organizer': 'Layout',
        'DAX Optimizer': 'DAX',
        'BI Bot': 'Bot'
    }

    for full_name, short_name in app_short_names.items():
        if full_name in user_stats.columns:
            user_stats[short_name] = user_stats[full_name].fillna(0).astype(int)
            user_stats = user_stats.drop(columns=[full_name])
        else:
            user_stats[short_name] = 0

    user_stats['primera_vez'] = user_stats['primera_vez'].dt.strftime('%Y-%m-%d %H:%M')
    user_stats['ultima_vez'] = user_stats['ultima_vez'].dt.strftime('%Y-%m-%d %H:%M')

    # Reorder
    cols_order = ['username', 'sesiones', 'eventos', 'primera_vez', 'ultima_vez',
                  'Analyzer', 'DocGen', 'Layout', 'DAX', 'Bot']
    user_stats = user_stats[cols_order]
    user_stats.columns = ['Usuario', 'Sesiones', 'Eventos Total', 'Primera Actividad',
                          'Ultima Actividad', 'Analyzer', 'DocGen', 'Layout', 'DAX', 'Bot']
    user_stats = user_stats.sort_values('Eventos Total', ascending=False)

    st.dataframe(user_stats, use_container_width=True, hide_index=True, height=350)

    st.markdown("---")

    # ============================================================
    # ACTIVITY OVER TIME
    # ============================================================
    st.markdown("### 📅 Actividad Temporal")

    daily_events = df_filtered.groupby('date').size().reset_index(name='eventos')
    daily_events['date'] = pd.to_datetime(daily_events['date'])

    fig = px.line(daily_events, x='date', y='eventos',
                  title='Eventos por Dia',
                  markers=True)
    fig.update_traces(line_color='#0451E4')
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ============================================================
    # APP USAGE
    # ============================================================
    st.markdown("### 🚀 Uso por Aplicacion")

    app_usage = df_filtered[df_filtered['app'] != 'Sistema'].groupby('app').size().reset_index(name='eventos')
    app_usage = app_usage.sort_values('eventos', ascending=False)

    if not app_usage.empty:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.dataframe(app_usage, use_container_width=True, hide_index=True)
        with col2:
            fig = px.pie(app_usage, values='eventos', names='app',
                         title='Distribucion de Uso',
                         color_discrete_sequence=['#0451E4', '#3B82F6', '#60A5FA', '#93C5FD', '#DBEAFE'])
            fig.update_layout(height=380)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ============================================================
    # RECENT EVENTS
    # ============================================================
    st.markdown("### 🕐 Ultimos Eventos")

    recent_events = df_filtered.sort_values('timestamp', ascending=False).head(100)
    display_df = recent_events[['timestamp', 'username', 'hostname', 'event', 'session_id']].copy()
    display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    display_df.columns = ['Fecha/Hora', 'Usuario', 'Equipo', 'Evento', 'Session ID']

    st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)

    # ============================================================
    # EXPORT
    # ============================================================
    st.markdown("---")
    st.markdown("### 📥 Exportar Datos")

    csv = df_filtered.to_csv(index=False)
    st.download_button(
        label="Descargar CSV (con filtros aplicados)",
        data=csv,
        file_name=f"ypf_bi_monitor_usage_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

    # ============================================================
    # METHODOLOGY (transparency on how the score is built)
    # ============================================================
    st.markdown("---")
    _render_score_methodology()

    render_footer()


def _render_score_methodology():
    """Render de la sección 'Metodología del Score' — look corporativo claro YPF.

    Explica las 4 dimensiones de calidad con pesos, métricas que las alimentan
    y umbrales globales. Diseño sutil con paleta corporativa.
    """
    st.markdown("""
    <div style="display:flex; align-items:baseline; justify-content:space-between;
                margin-bottom:0.6rem;">
        <h3 style="color:#1E293B; font-family:'Fira Sans',sans-serif; margin:0;
                   font-weight:600; letter-spacing:-0.01em; font-size:1.05rem;">
            📐 Metodología del Score
        </h3>
        <span style="color:#94A3B8; font-size:0.7rem; letter-spacing:0.08em;
                     text-transform:uppercase; font-weight:500;
                     font-family:'Fira Sans',sans-serif;">
            v2.0 · 4 dimensiones
        </span>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("¿Cómo se construye la métrica de calidad?", expanded=False):
        st.markdown("""
        <p style="color:#475569; font-size:0.88rem; line-height:1.65;
                  margin:0 0 1rem 0; font-family:'Fira Sans',sans-serif;">
            El score global del Power BI Analyzer se calcula como un
            <strong style="color:#1E293B;">promedio ponderado de 4 dimensiones de calidad</strong>,
            cada una alimentada por métricas específicas medidas sobre el reporte. Las
            dimensiones reflejan los pilares de un reporte sostenible y mantenible.
        </p>
        """, unsafe_allow_html=True)

        dims = [
            {
                'label': 'Modelo Semántico',
                'weight': '35%',
                'desc': 'Cimiento del reporte. Mide la calidad estructural del diseño de datos.',
                'metrics': ['Cantidad de tablas', 'Relaciones totales',
                            'Relaciones bidireccionales', 'Columnas calculadas',
                            'Tamaño del modelo'],
            },
            {
                'label': 'DAX / Performance',
                'weight': '25%',
                'desc': 'Calidad de las medidas DAX y su impacto en el rendimiento del reporte.',
                'metrics': ['Medidas DAX complejas'],
            },
            {
                'label': 'Diseño del Reporte',
                'weight': '25%',
                'desc': 'Composición visual: densidad por página, filtros y assets embebidos.',
                'metrics': ['Visualizaciones por página', 'Filtros por página',
                            'Imágenes embebidas (MB)'],
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
                f'<li style="color:#475569; font-size:0.78rem; line-height:1.6; '
                f'margin-bottom:0.15rem; font-family:\'Fira Sans\',sans-serif;">{m}</li>'
                for m in dim['metrics']
            )
            with col:
                st.markdown(f"""
                <div style="background:#FFFFFF; border:1px solid #E2E8F0;
                            border-left:4px solid #0451E4; border-radius:0 8px 8px 0;
                            padding:1rem 1.1rem; height:100%;
                            box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                    <div style="display:inline-block; color:#0451E4; font-size:0.7rem;
                                letter-spacing:0.08em; font-weight:700;
                                padding:0.2rem 0.6rem; border-radius:6px;
                                background:rgba(4,81,228,0.08);
                                border:1px solid rgba(4,81,228,0.18);
                                margin-bottom:0.65rem;
                                font-family:'Fira Sans',sans-serif;">
                        {dim['weight']}
                    </div>
                    <div style="color:#1E293B; font-family:'Fira Sans',sans-serif;
                                font-size:0.9rem; font-weight:600; letter-spacing:-0.01em;
                                line-height:1.3; margin-bottom:0.4rem;">
                        {dim['label']}
                    </div>
                    <p style="color:#64748B; font-size:0.78rem; line-height:1.6;
                              margin:0 0 0.7rem 0; font-family:'Fira Sans',sans-serif;">
                        {dim['desc']}
                    </p>
                    <div style="color:#94A3B8; font-size:0.65rem; letter-spacing:0.1em;
                                text-transform:uppercase; margin-bottom:0.35rem;
                                font-weight:600; font-family:'Fira Sans',sans-serif;">
                        Métricas
                    </div>
                    <ul style="margin:0; padding-left:1rem;">{metrics_html}</ul>
                </div>
                """, unsafe_allow_html=True)

        # Thresholds block
        st.markdown("""
        <div style="margin-top:1.25rem; background:#F8FAFC; border:1px solid #E2E8F0;
                    border-radius:8px; padding:1rem 1.25rem;">
            <div style="color:#64748B; font-size:0.7rem; letter-spacing:0.1em;
                        text-transform:uppercase; margin-bottom:0.65rem;
                        font-weight:600; font-family:'Fira Sans',sans-serif;">
                Umbrales de Score Global
            </div>
            <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:0.75rem;">
                <div style="text-align:center;">
                    <div style="color:#10B981; font-size:1.15rem; font-weight:700;
                                font-family:'Fira Sans',sans-serif;">90 – 100</div>
                    <div style="color:#64748B; font-size:0.75rem; margin-top:0.15rem;
                                font-family:'Fira Sans',sans-serif;">Excelente</div>
                </div>
                <div style="text-align:center;">
                    <div style="color:#0451E4; font-size:1.15rem; font-weight:700;
                                font-family:'Fira Sans',sans-serif;">75 – 89</div>
                    <div style="color:#64748B; font-size:0.75rem; margin-top:0.15rem;
                                font-family:'Fira Sans',sans-serif;">Bueno</div>
                </div>
                <div style="text-align:center;">
                    <div style="color:#F59E0B; font-size:1.15rem; font-weight:700;
                                font-family:'Fira Sans',sans-serif;">60 – 74</div>
                    <div style="color:#64748B; font-size:0.75rem; margin-top:0.15rem;
                                font-family:'Fira Sans',sans-serif;">Atención</div>
                </div>
                <div style="text-align:center;">
                    <div style="color:#EF4444; font-size:1.15rem; font-weight:700;
                                font-family:'Fira Sans',sans-serif;">0 – 59</div>
                    <div style="color:#64748B; font-size:0.75rem; margin-top:0.15rem;
                                font-family:'Fira Sans',sans-serif;">Crítico</div>
                </div>
            </div>
            <p style="color:#94A3B8; font-size:0.72rem; line-height:1.6;
                      margin:0.85rem 0 0 0; text-align:center;
                      font-family:'Fira Sans',sans-serif;">
                Umbrales alineados con el sistema del Power BI Fixer para mantener
                consistencia entre las herramientas de la suite.
            </p>
        </div>
        """, unsafe_allow_html=True)

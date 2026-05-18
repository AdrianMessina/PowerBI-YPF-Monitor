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
    render_app_header(
        "Usage Dashboard",
        "Metricas y estadisticas de uso de YPF BI Monitor",
        "1.0"
    )

    # Require admin authentication
    auth = Authenticator()
    if not auth.require_auth(admin_only=True):
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

    # User summary table
    user_stats = df.groupby('username').agg(
        sesiones=('session_id', 'nunique'),
        eventos=('event', 'count'),
        primera_vez=('timestamp', 'min'),
        ultima_vez=('timestamp', 'max')
    ).reset_index()
    user_stats['primera_vez'] = user_stats['primera_vez'].dt.strftime('%Y-%m-%d %H:%M')
    user_stats['ultima_vez'] = user_stats['ultima_vez'].dt.strftime('%Y-%m-%d %H:%M')
    user_stats.columns = ['Usuario', 'Sesiones', 'Eventos', 'Primera Actividad', 'Ultima Actividad']
    user_stats = user_stats.sort_values('Eventos', ascending=False)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.dataframe(user_stats, use_container_width=True, hide_index=True)

    with col2:
        fig = px.bar(user_stats, x='Usuario', y='Eventos',
                     title='Eventos por Usuario',
                     color='Sesiones',
                     color_continuous_scale=['#E6E6E6', '#0451E4'])
        fig.update_layout(height=400)
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
                         title='Uso por Aplicacion',
                         color_discrete_sequence=['#0451E4', '#000000', '#3C3C3C', '#AAAAAA', '#E6E6E6'])
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aun no hay suficientes datos para analisis por app")

    st.markdown("---")

    # Recent events (respects user filter)
    st.markdown("### Ultimos Eventos")

    recent_events = df_filtered.sort_values('timestamp', ascending=False).head(50)
    display_df = recent_events[['timestamp', 'username', 'hostname', 'event', 'session_id']].copy()
    display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    display_df.columns = ['Fecha/Hora', 'Usuario', 'Equipo', 'Evento', 'Session ID']

    st.dataframe(display_df, use_container_width=True, hide_index=True)

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

    render_footer()

"""
Usage Dashboard - Metricas de Uso de YPF BI Monitor
Herramienta interna con acceso restringido por email corporativo
"""

import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

from apps_core.layout_core.shared_styles import render_app_header, render_footer


# Authorized users whitelist (emails or Windows usernames)
AUTHORIZED_USERS = [
    "se43617",
    "se46958",
    "nicolas.ursino",
    "se42998",
    "se41714",
    "se48659",
    "se48762",
]


def _get_current_user() -> str:
    """Get current Windows username (lowercase for comparison)."""
    return os.environ.get('USERNAME', os.environ.get('USER', '')).lower()


def _check_admin_access() -> bool:
    """
    Verify admin access via email whitelist or manual login.
    Returns True if authenticated, False otherwise.
    """
    # Check if already authenticated in this session
    if st.session_state.get('admin_authenticated', False):
        return True

    # Auto-authenticate if Windows username matches whitelist
    current_user = _get_current_user()
    if current_user in AUTHORIZED_USERS:
        st.session_state.admin_authenticated = True
        st.session_state.admin_user = current_user
        return True

    # Manual login for users not auto-detected
    st.markdown("""
    <div style="max-width: 450px; margin: 2rem auto; padding: 2rem;
                background: #f8f9fa; border-radius: 10px;
                border: 1px solid #E2E8F0; text-align: center;">
        <h3 style="color: #1E293B; margin-bottom: 0.5rem;
                   font-family: 'Fira Sans', sans-serif;">Acceso Restringido</h3>
        <p style="color: #666; font-size: 0.9rem; font-family: 'Fira Sans', sans-serif;">
            Esta herramienta es solo para usuarios autorizados.<br>
            Ingresa tu email corporativo para verificar acceso.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        email_input = st.text_input(
            "Email corporativo",
            key="admin_email_input",
            placeholder="seXXXXX@grupo.ypf.com"
        )

        if st.button("Verificar acceso", use_container_width=True, key="admin_login_btn"):
            if email_input:
                # Extract username from email (e.g. "se46958" from "se46958@grupo.ypf.com")
                email_user = email_input.strip().lower().split('@')[0]
                if email_user in AUTHORIZED_USERS:
                    st.session_state.admin_authenticated = True
                    st.session_state.admin_user = email_user
                    st.rerun()
                else:
                    st.error("Tu email no tiene acceso a esta herramienta.")
            else:
                st.warning("Ingresa tu email corporativo.")

    return False


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

    # Admin authentication gate
    if not _check_admin_access():
        render_footer()
        return

    # Show logged-in user and logout option
    admin_user = st.session_state.get('admin_user', _get_current_user())
    col1, col2, col3 = st.columns([4, 2, 1])
    with col2:
        st.markdown(f"<p style='color: #666; font-size: 0.85rem; padding-top: 0.5rem; text-align: right;'>"
                    f"Usuario: <strong>{admin_user}</strong></p>", unsafe_allow_html=True)
    with col3:
        if st.button("Cerrar sesion", key="admin_logout"):
            st.session_state.admin_authenticated = False
            st.session_state.pop('admin_user', None)
            st.rerun()

    # Find log files
    logs_dir = Path(__file__).parent.parent / "logs"

    if not logs_dir.exists():
        st.warning("No se encontraron logs de uso todavia.")
        st.info("Los logs se crearan automaticamente cuando uses las aplicaciones.")
        render_footer()
        return

    log_files = list(logs_dir.glob("usage_*.jsonl"))

    if not log_files:
        st.warning("No hay datos de uso disponibles todavia.")
        st.info("Usa las aplicaciones y luego regresa aqui para ver las estadisticas.")
        render_footer()
        return

    # Read all logs
    all_events = []
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        event = json.loads(line)
                        all_events.append(event)
        except Exception as e:
            st.error(f"Error leyendo {log_file.name}: {e}")

    if not all_events:
        st.warning("No se pudieron leer los eventos de uso.")
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

"""
Power BI Analyzer - Integrado en YPF BI Monitor
Replica funcionalidad completa de Power BI Analyzer v1.1
"""

import streamlit as st
import sys
import os
from pathlib import Path
import tempfile
import re
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import yaml
import time


def render_app(logger):
    """
    Wrapper para Power BI Analyzer integrado en YPF BI Monitor

    Args:
        logger: Logger de la suite para tracking de uso
    """

    # Imports absolutos - NO requiere manipular sys.path
    try:
        from apps_core.analyzer_core.core import analyze_powerbi_file
        from apps_core.analyzer_core.core.report_generator import ReportGenerator
    except Exception as e:
        st.error(f"❌ Error importando módulos core: {str(e)}")
        with st.expander("🔍 Ver stacktrace completo"):
            import traceback
            st.code(traceback.format_exc())
        st.stop()

    # Variable global para logger
    usage_logger = logger
    LOGGING_ENABLED = logger is not None

    # Import shared styles (replaces app-specific CSS)
    from apps_core.layout_core.shared_styles import render_app_header, render_footer

    # Minimal app-specific CSS (functional styles only - layout comes from shared CSS)
    st.markdown("""
        <style>
        /* Power BI Analyzer - Functional CSS variables */
        :root {
            --success-color: #10B981;
            --warning-color: #F59E0B;
            --critical-color: #EF4444;
        }

        /* Score colors */
        .score-excellent { color: var(--success-color); }
        .score-good { color: #00D4AA; }
        .score-warning { color: var(--warning-color); }
        .score-poor { color: var(--critical-color); }

        /* Badges */
        .badge {
            padding: 0.375rem 0.75rem;
            border-radius: 8px;
            font-size: 0.875rem;
            font-weight: 600;
            display: inline-block;
        }
        .badge-success {
            background-color: rgba(16, 185, 129, 0.1);
            color: var(--success-color);
            border: 1px solid rgba(16, 185, 129, 0.2);
        }
        .badge-warning {
            background-color: rgba(245, 158, 11, 0.1);
            color: var(--warning-color);
            border: 1px solid rgba(245, 158, 11, 0.2);
        }
        .badge-danger {
            background-color: rgba(239, 68, 68, 0.1);
            color: var(--critical-color);
            border: 1px solid rgba(239, 68, 68, 0.2);
        }

        /* Metric cards */
        .metric-card {
            background: white;
            padding: 1.75rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border-left: 4px solid #0451E4;
        }

        /* Tabs - YPF styled */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #E6E6E6;
            padding: 0.5rem;
            border-radius: 12px;
            border-bottom: 3px solid #0451E4;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #0451E4 0%, #0340B8 100%);
            color: #FFFFFF;
            box-shadow: 0 2px 8px rgba(4, 81, 228, 0.3);
        }

        /* Loader spinner */
        .ypf-loader-container {
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: center;
            padding: 1.5rem;
            background: rgba(4, 81, 228, 0.03);
            border-radius: 12px;
            border: 2px solid #0451E4;
            gap: 1rem;
        }
        .ypf-loader {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #000000;
            border-right: 4px solid #0451E4;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .ypf-loader-text {
            margin: 0;
            font-size: 1rem;
            font-weight: 600;
            color: #000000;
        }
        </style>
    """, unsafe_allow_html=True)
    
    
    def get_score_color(score):
        """Retorna el color según el score - Paleta moderna"""
        if score >= 90:
            return "#10B981"  # Verde moderno
        elif score >= 75:
            return "#00D4AA"  # Verde menta
        elif score >= 60:
            return "#F59E0B"  # Ámbar
        else:
            return "#EF4444"  # Rojo suave
    
    
    def get_score_label(score):
        """Retorna la etiqueta según el score"""
        if score >= 90:
            return "Excelente"
        elif score >= 75:
            return "Bueno"
        elif score >= 60:
            return "Mejorable"
        else:
            return "Requiere Atención"
    
    
    def sanitize_filename(filename):
        """
        Sanitiza un nombre de archivo removiendo caracteres problemáticos
        y preservando tildes y espacios
    
        Args:
            filename: Nombre del archivo a sanitizar
    
        Returns:
            Nombre de archivo sanitizado
        """
        # Remover extensión si existe
        name_without_ext = filename.replace('.pbix', '').replace('.pbip', '')
    
        # Remover caracteres especiales problemáticos pero preservar tildes y espacios
        # Permitidos: letras (con tildes), números, espacios, guiones, guiones bajos, paréntesis
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', name_without_ext)
    
        # Limitar longitud del nombre (Windows tiene límite de 255 caracteres)
        max_length = 100
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
    
        # Remover espacios múltiples
        sanitized = re.sub(r'\s+', ' ', sanitized)
    
        # Remover espacios al inicio y final
        sanitized = sanitized.strip()
    
        return sanitized
    
    
    def create_score_gauge(score):
        """Crea un gauge chart moderno y minimalista para el score"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={
                'text': "Score General",
                'font': {'size': 22, 'family': 'Inter, sans-serif', 'color': '#2C3E50'}
            },
            number={
                'font': {'size': 48, 'family': 'Inter, sans-serif', 'color': get_score_color(score)},
                'suffix': "/100"
            },
            gauge={
                'axis': {
                    'range': [None, 100],
                    'tickwidth': 2,
                    'tickcolor': "#E1E8ED",
                    'tickfont': {'size': 12, 'color': '#6B7280'}
                },
                'bar': {
                    'color': get_score_color(score),
                    'thickness': 0.75
                },
                'bgcolor': "#F7F9FC",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 60], 'color': 'rgba(239, 68, 68, 0.1)'},
                    {'range': [60, 75], 'color': 'rgba(245, 158, 11, 0.1)'},
                    {'range': [75, 90], 'color': 'rgba(0, 212, 170, 0.1)'},
                    {'range': [90, 100], 'color': 'rgba(16, 185, 129, 0.1)'}
                ],
                'threshold': {
                    'line': {'color': "#10B981", 'width': 3},
                    'thickness': 0.8,
                    'value': 90
                }
            }
        ))

        fig.update_layout(
            height=320,
            margin=dict(l=30, r=30, t=60, b=30),
            paper_bgcolor="rgba(0,0,0,0)",
            font={'color': "#2C3E50", 'family': "Inter, sans-serif"}
        )

        return fig


    def render_category_breakdown(category_scores: dict):
        """Render del breakdown del score por las 4 dimensiones de calidad.

        Cada categoría muestra peso, score y status badge. Look corporativo YPF.
        """
        if not category_scores:
            return

        ordered_keys = ['modelo_semantico', 'dax_performance', 'diseno_reporte', 'gobernanza']
        ordered = [(k, category_scores[k]) for k in ordered_keys if k in category_scores]

        # Status -> (label, color principal, color fondo)
        status_palette = {
            'excellent':   ('Excelente', '#10B981', 'rgba(16,185,129,0.10)'),
            'good':        ('Bueno',     '#0451E4', 'rgba(4,81,228,0.10)'),
            'warning':     ('Atención',  '#F59E0B', 'rgba(245,158,11,0.10)'),
            'poor':        ('Crítico',   '#EF4444', 'rgba(239,68,68,0.10)'),
            'unavailable': ('N/D',       '#94A3B8', 'rgba(148,163,184,0.10)'),
        }

        st.markdown("""
        <div style="display:flex; align-items:baseline; justify-content:space-between;
                    margin: 0.25rem 0 0.85rem 0;">
            <h4 style="color:#1E293B; font-family:'Fira Sans',sans-serif;
                       font-size:1rem; font-weight:600; margin:0; letter-spacing:-0.01em;">
                Score por Dimensión
            </h4>
            <span style="color:#94A3B8; font-size:0.7rem; letter-spacing:0.08em;
                         text-transform:uppercase; font-weight:500;
                         font-family:'Fira Sans',sans-serif;">
                4 dimensiones · promedio ponderado
            </span>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(len(ordered))
        for col, (cat_key, cat) in zip(cols, ordered):
            score = cat.get('score')
            status = cat.get('status', 'unavailable')
            label_status, color_hex, color_bg = status_palette.get(status, status_palette['unavailable'])
            weight_pct = int(round(cat.get('weight', 0) * 100))
            score_display = f"{int(round(score))}" if score is not None else "—"
            bar_width = max(0, min(100, score if score is not None else 0))

            with col:
                st.markdown(f"""
                <div style="background:#FFFFFF; border:1px solid #E2E8F0;
                            border-left:4px solid #0451E4; border-radius:0 8px 8px 0;
                            padding:1rem 1.1rem; height:100%;
                            box-shadow:0 2px 8px rgba(0,0,0,0.04); position:relative;">
                    <div style="display:flex; align-items:center; justify-content:space-between;
                                margin-bottom:0.6rem;">
                        <span style="color:#0451E4; font-size:0.7rem; letter-spacing:0.08em;
                                     font-weight:700; padding:0.18rem 0.55rem; border-radius:6px;
                                     background:rgba(4,81,228,0.08);
                                     border:1px solid rgba(4,81,228,0.18);
                                     font-family:'Fira Sans',sans-serif;">
                            {weight_pct}%
                        </span>
                        <span style="color:{color_hex}; font-size:0.65rem; letter-spacing:0.08em;
                                     font-weight:600; padding:0.18rem 0.5rem; border-radius:9999px;
                                     background:{color_bg}; text-transform:uppercase;
                                     font-family:'Fira Sans',sans-serif;">
                            {label_status}
                        </span>
                    </div>
                    <div style="color:#1E293B; font-family:'Fira Sans',sans-serif;
                                font-size:0.88rem; font-weight:600; letter-spacing:-0.01em;
                                line-height:1.3; margin-bottom:0.55rem; min-height:2.3rem;">
                        {cat['label']}
                    </div>
                    <div style="color:{color_hex}; font-family:'Fira Sans',sans-serif;
                                font-size:2rem; font-weight:700; line-height:1;
                                margin-bottom:0.65rem;">
                        {score_display}<span style="color:#94A3B8; font-size:0.9rem;
                                                     font-weight:500; margin-left:2px;">/100</span>
                    </div>
                    <div style="background:#F1F5F9; border-radius:9999px; height:6px;
                                overflow:hidden;">
                        <div style="width:{bar_width}%; height:100%;
                                    background:linear-gradient(90deg, {color_hex} 0%, {color_hex}dd 100%);
                                    border-radius:9999px;
                                    transition:width 400ms cubic-bezier(0.16,1,0.3,1);"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)


    def create_metrics_comparison_chart(metric_scores, metrics):
        """Crea un gráfico de barras moderno comparando valores actuales vs thresholds"""
    
        metric_names = {
            'visualizations_per_page': 'Visuales/Página',
            'filters_per_page': 'Filtros/Página',
            'custom_visuals': 'Custom Visuals',
            'embedded_images_mb': 'Imágenes (MB)',
            'total_pages': 'Páginas',
            'dax_measures_complex': 'DAX Complejo',
            'tables_in_model': 'Tablas',
            'relationships': 'Relaciones',
            'bidirectional_relationships': 'Rel. Bidireccional',
            'calculated_columns': 'Columnas Calc.',
            'model_size_mb': 'Tamaño (MB)',
        }
    
        # Preparar datos
        labels = []
        current_values = []
        threshold_values = []
        colors = []
    
        # Cargar thresholds
        config_path = os.path.join(Path(__file__).parent.parent, 'config', 'analyzer_thresholds.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        thresholds = config.get('thresholds', {})
    
        for metric_key, metric_data in metric_scores.items():
            label = metric_names.get(metric_key, metric_key)
            labels.append(label)
            current_values.append(metric_data['value'])
    
            # Obtener el threshold "good"
            threshold = thresholds.get(metric_key, {}).get('good', 0)
            threshold_values.append(threshold)
    
            if metric_data['status'] == 'good':
                colors.append('#10B981')
            elif metric_data['status'] == 'warning':
                colors.append('#F59E0B')
            else:
                colors.append('#EF4444')
    
        # Crear gráfico con dos barras: actual y threshold
        fig = go.Figure()
    
        fig.add_trace(go.Bar(
            name='Valor Actual',
            x=labels,
            y=current_values,
            marker=dict(
                color=colors,
                line=dict(color='rgba(255,255,255,0.8)', width=1)
            ),
            text=[f'{v:.1f}' for v in current_values],
            textposition='outside',
            textfont=dict(size=11, family='Inter, sans-serif', color='#2C3E50'),
            hovertemplate='<b>%{x}</b><br>Actual: %{y:.1f}<extra></extra>'
        ))
    
        fig.add_trace(go.Bar(
            name='Threshold Óptimo',
            x=labels,
            y=threshold_values,
            marker=dict(
                color='#E1E8ED',
                line=dict(color='#9CA3AF', width=1),
                pattern_shape="/"
            ),
            opacity=0.6,
            text=[f'{v:.1f}' for v in threshold_values],
            textposition='outside',
            textfont=dict(size=10, family='Inter, sans-serif', color='#6B7280'),
            hovertemplate='<b>%{x}</b><br>Threshold: %{y:.1f}<extra></extra>'
        ))
    
        fig.update_layout(
            title=dict(
                text="Métricas: Comparativa Valor Actual vs. Threshold Óptimo",
                font=dict(size=18, family='Inter, sans-serif', color='#2C3E50'),
                x=0.05
            ),
            xaxis=dict(
                title="",
                tickfont=dict(size=11, family='Inter, sans-serif', color='#6B7280'),
                showgrid=False
            ),
            yaxis=dict(
                title="Valor",
                titlefont=dict(size=12, family='Inter, sans-serif', color='#6B7280'),
                tickfont=dict(size=11, family='Inter, sans-serif', color='#6B7280'),
                gridcolor='#F3F4F6',
                showline=False
            ),
            height=520,
            barmode='group',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=11, family='Inter, sans-serif', color='#6B7280'),
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='#E1E8ED',
                borderwidth=1
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=50, r=50, t=80, b=50),
            bargap=0.2,
            bargroupgap=0.1
        )
    
        return fig
    
    
    def create_problems_distribution_pie(metric_scores):
        """Crea un gráfico circular mostrando % de problemas por categoría CON DETALLE"""
    
        problem_categories = {}
        problem_details = {}  # Nuevo: detalle por categoría
    
        metric_categories = {
            'visualizations_per_page': 'Visualizaciones',
            'filters_per_page': 'Filtros',
            'custom_visuals': 'Custom Visuals',
            'embedded_images_mb': 'Imágenes',
            'total_pages': 'Páginas',
            'dax_measures_complex': 'Complejidad DAX',
            'tables_in_model': 'Modelo de Datos',
            'relationships': 'Modelo de Datos',
            'bidirectional_relationships': 'Relaciones',
            'calculated_columns': 'Columnas Calculadas',
            'model_size_mb': 'Tamaño del Modelo',
        }
    
        severity_weights = {
            'critical': 3,
            'warning': 2,
            'info': 1
        }
    
        for metric_key, metric_data in metric_scores.items():
            if metric_data['status'] in ['warning', 'critical']:
                category = metric_categories.get(metric_key, 'Otros')
    
                # Contar problemas
                problem_categories[category] = problem_categories.get(category, 0) + 1
    
                # Guardar detalles
                if category not in problem_details:
                    problem_details[category] = {
                        'count': 0,
                        'severities': [],
                        'impact_scores': []
                    }
    
                problem_details[category]['count'] += 1
                problem_details[category]['severities'].append(metric_data['status'])
    
                # Calcular impacto aproximado en el score
                impact = (100 - metric_data['score']) * severity_weights.get(metric_data['status'], 1)
                problem_details[category]['impact_scores'].append(impact)
    
        if not problem_categories:
            return None, None
    
        # Calcular estadísticas por categoría
        category_stats = []
        for category, count in problem_categories.items():
            details = problem_details[category]
            critical_count = details['severities'].count('critical')
            warning_count = details['severities'].count('warning')
            avg_impact = sum(details['impact_scores']) / len(details['impact_scores']) if details['impact_scores'] else 0
    
            category_stats.append({
                'Categoría': category,
                'Problemas': count,
                'Críticos': critical_count,
                'Advertencias': warning_count,
                'Impacto Promedio': f"{avg_impact:.1f}"
            })
    
        # Crear gráfico moderno
        total_problems = sum(problem_categories.values())
    
        # Paleta de colores moderna
        modern_colors = ['#4A90E2', '#6C63FF', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']
    
        fig = go.Figure(data=[go.Pie(
            labels=list(problem_categories.keys()),
            values=list(problem_categories.values()),
            hole=0.5,
            marker=dict(
                colors=modern_colors[:len(problem_categories)],
                line=dict(color='white', width=3)
            ),
            textinfo='label+percent',
            textfont=dict(size=12, family='Inter, sans-serif', color='white'),
            hovertemplate='<b>%{label}</b><br>Problemas: %{value}<br>Porcentaje: %{percent}<extra></extra>',
            pull=[0.05 if v == max(problem_categories.values()) else 0 for v in problem_categories.values()]
        )])
    
        fig.update_layout(
            title=dict(
                text=f"Distribución de Problemas por Categoría",
                font=dict(size=18, family='Inter, sans-serif', color='#2C3E50'),
                x=0.5,
                xanchor='center'
            ),
            height=450,
            annotations=[dict(
                text=f'<b>{total_problems}</b><br><span style="font-size:14px;">Problemas</span>',
                x=0.5, y=0.5,
                font=dict(size=24, family='Inter, sans-serif', color='#2C3E50'),
                showarrow=False
            )],
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05,
                font=dict(size=11, family='Inter, sans-serif', color='#6B7280')
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=120, t=60, b=20)
        )
    
        return fig, category_stats
    
    
    def create_weight_distribution_chart(metrics):
        """Crea un gráfico mostrando la distribución del peso del reporte por componente"""
    
        # FIX v1.1: Si el modelo no está disponible, no intentar crear el gráfico
        model_available = metrics.get('model_analysis_available', True)
        if not model_available:
            return None
    
        # Estimaciones aproximadas del peso por componente
        # FIX v1.1: Usar 'or 0' para manejar None correctamente
        model_size_mb = metrics.get('model_size_mb') or 0
        images_mb = metrics.get('embedded_images_mb') or 0
        total_tables = metrics.get('total_tables') or 0
        total_measures = metrics.get('total_measures') or 0
        calculated_columns = metrics.get('calculated_columns') or 0
        total_visuals = metrics.get('total_visuals') or 0
    
        # Estimaciones aproximadas (en MB)
        # Las tablas representan la mayor parte del tamaño del modelo
        tables_weight = model_size_mb * 0.70 if model_size_mb > 0 else total_tables * 10
        measures_weight = total_measures * 0.01  # ~10KB por medida
        calc_columns_weight = calculated_columns * 0.05  # ~50KB por columna calculada
        visuals_weight = total_visuals * 0.02  # ~20KB por visual
        images_weight = images_mb
    
        # Si hay model_size pero no hay desglose, ajustar proporcionalmente
        if model_size_mb > 0:
            total_estimated = tables_weight + measures_weight + calc_columns_weight + visuals_weight + images_weight
            if total_estimated > 0:
                # Ajustar para que sume el tamaño real del modelo
                adjustment_factor = model_size_mb / total_estimated
                tables_weight *= adjustment_factor
                measures_weight *= adjustment_factor
                calc_columns_weight *= adjustment_factor
                visuals_weight *= adjustment_factor
    
        components = {
            'Tablas (Datos)': tables_weight,
            'Medidas DAX': measures_weight,
            'Columnas Calculadas': calc_columns_weight,
            'Visualizaciones': visuals_weight,
            'Imágenes': images_weight
        }
    
        # Filtrar componentes con peso > 0
        components = {k: v for k, v in components.items() if v > 0}
    
        if not components or sum(components.values()) == 0:
            return None
    
        # Calcular porcentajes
        total_weight = sum(components.values())
        percentages = {k: (v / total_weight * 100) for k, v in components.items()}
    
        # Colores modernos y armoniosos
        colors = {
            'Tablas (Datos)': '#4A90E2',
            'Medidas DAX': '#6C63FF',
            'Columnas Calculadas': '#10B981',
            'Visualizaciones': '#F59E0B',
            'Imágenes': '#EF4444'
        }
    
        fig = go.Figure(data=[go.Pie(
            labels=list(components.keys()),
            values=list(components.values()),
            hole=0.5,
            marker=dict(
                colors=[colors.get(k, '#9CA3AF') for k in components.keys()],
                line=dict(color='white', width=3)
            ),
            textinfo='label+percent',
            textfont=dict(size=12, family='Inter, sans-serif', color='white'),
            hovertemplate='<b>%{label}</b><br>Peso: %{value:.1f} MB<br>Porcentaje: %{percent}<extra></extra>',
            pull=[0.05 if v == max(components.values()) else 0 for v in components.values()]
        )])
    
        fig.update_layout(
            title=dict(
                text=f"Distribución del Peso del Reporte",
                font=dict(size=18, family='Inter, sans-serif', color='#2C3E50'),
                x=0.5,
                xanchor='center'
            ),
            height=450,
            annotations=[dict(
                text=f'<b>{total_weight:.1f}</b><br><span style="font-size:14px;">MB Total</span>',
                x=0.5, y=0.5,
                font=dict(size=24, family='Inter, sans-serif', color='#2C3E50'),
                showarrow=False
            )],
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05,
                font=dict(size=11, family='Inter, sans-serif', color='#6B7280')
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=120, t=60, b=20)
        )
    
        return fig
    
    
    def safe_metric_value(value, default="N/A"):
        """
        Convierte un valor de métrica a string seguro para mostrar
    
        Args:
            value: Valor de la métrica (puede ser None)
            default: Valor por defecto si es None
        Returns:
            Valor formateado o default
        """
        if value is None:
            return default
        return value
    
    
    def display_metric_with_threshold(label, value, threshold_config, reverse_logic=False):
        """
        Muestra una métrica con comparativa visual de thresholds
    
        Args:
            label: Etiqueta de la métrica
            value: Valor actual (puede ser None si no disponible)
            threshold_config: Configuración de thresholds (good, warning, critical)
            reverse_logic: Si True, valores menores son mejores (ej: model_size_mb)
        """
        # Manejar valores no disponibles
        if value is None:
            st.metric(label, "N/A")
            st.info("⚠️ Métrica no disponible para este archivo.")
            return
    
        if not threshold_config:
            st.metric(label, value)
            return
    
        good = threshold_config.get('good', 0)
        warning = threshold_config.get('warning', 0)
        critical = threshold_config.get('critical', 0)
    
        # Determinar estado
        if not reverse_logic:
            # Valores menores son mejores (ej: visualizations_per_page)
            if value <= good:
                status = "✅ BUENO"
                color = "green"
                delta_msg = f"Dentro del óptimo (≤{good})"
            elif value <= warning:
                status = "⚠️ ADVERTENCIA"
                color = "orange"
                delta_msg = f"{value - good} sobre el óptimo"
            else:
                status = "🔴 CRÍTICO"
                color = "red"
                delta_msg = f"{value - warning} sobre el límite"
        else:
            # Valores mayores son mejores (ej: model_size_mb donde good es el máximo permitido)
            if value <= good:
                status = "✅ BUENO"
                color = "green"
                delta_msg = f"Dentro del óptimo (≤{good})"
            elif value <= warning:
                status = "⚠️ ADVERTENCIA"
                color = "orange"
                delta_msg = f"{value - good} sobre el óptimo"
            else:
                status = "🔴 CRÍTICO"
                color = "red"
                delta_msg = f"{value - warning} sobre el límite"
    
        # Mostrar métrica con estado
        col1, col2 = st.columns([2, 1])
        with col1:
            st.metric(label, value)
        with col2:
            st.markdown(f"<p style='color: {color}; font-weight: bold; margin-top: 15px;'>{status}</p>", unsafe_allow_html=True)
    
        # Mostrar thresholds y distancia
        with st.expander(f"📊 Ver thresholds de {label}"):
            st.write(f"**Óptimo:** ≤ {good}")
            st.write(f"**Advertencia:** {good} - {warning}")
            st.write(f"**Crítico:** > {warning}")
            st.write(f"**Situación actual:** {delta_msg}")
    
            if threshold_config.get('recommendation'):
                st.info(f"💡 {threshold_config['recommendation']}")
    
    
    def display_detailed_metrics(result):
        """Muestra el desglose detallado de métricas con ubicación y THRESHOLDS"""
    
        metrics = result['metrics']
    
        # Obtener configuración de thresholds
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'analyzer_thresholds.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        thresholds = config.get('thresholds', {})
    
        st.markdown("### 📊 Desglose Detallado de Métricas")
    
        # Crear tabs para diferentes categorías
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔢 Modelo de Datos",
            "📐 Medidas DAX",
            "🔗 Relaciones",
            "📄 Visualizaciones"
        ])
    
        with tab1:
            col1, col2 = st.columns(2)
    
            with col1:
                st.markdown("#### Tablas del Modelo")
                # Usar nueva función con thresholds
                display_metric_with_threshold(
                    "Total de Tablas",
                    metrics.get('total_tables', 0),
                    thresholds.get('tables_in_model')
                )
    
                st.markdown("---")
    
                display_metric_with_threshold(
                    "Columnas Calculadas",
                    metrics.get('calculated_columns', 0),
                    thresholds.get('calculated_columns')
                )
    
                st.markdown("---")
                st.metric("Tablas Calculadas", metrics.get('calculated_tables', 0))
    
                # Detalles de columnas calculadas
                calc_cols_detail = metrics.get('calculated_columns_detail', [])
                if calc_cols_detail:
                    with st.expander(f"📋 Ver detalle de {len(calc_cols_detail)} columnas calculadas"):
                        for col_info in calc_cols_detail[:10]:  # Mostrar primeras 10
                            st.write(f"**{col_info['name']}** ({col_info['table']}) - {col_info['size_kb']:.2f} KB")
    
                # Columnas por tabla
                columns_by_table = metrics.get('columns_by_table', {})
                if columns_by_table:
                    st.markdown("**Top 5 Tablas por Columnas:**")
                    for table, count in sorted(columns_by_table.items(), key=lambda x: x[1], reverse=True)[:5]:
                        st.write(f"- {table}: {count} columnas")
    
            with col2:
                st.markdown("#### Configuración del Modelo")
    
                auto_dt = metrics.get('auto_date_time_enabled', 'Desconocido')
                if auto_dt == 'Sí':
                    st.warning(f"⚠️ Auto Date/Time: **{auto_dt}**")
                    st.info("💡 Desactiva Auto Date/Time y usa una tabla de calendario personalizada")
                else:
                    st.success(f"✅ Auto Date/Time: **{auto_dt}**")
    
                st.markdown("---")
    
                size_mb = metrics.get('model_size_mb', 0)
                display_metric_with_threshold(
                    "Tamaño del Modelo (MB)",
                    round(size_mb, 1),
                    thresholds.get('model_size_mb'),
                    reverse_logic=True
                )
    
                if 'model_size_note' in metrics:
                    st.info(metrics['model_size_note'])
    
        with tab2:
            st.markdown("#### Medidas DAX por Tabla")
    
            total_measures = metrics.get('total_measures', 0)
            complex_measures = metrics.get('complex_dax_measures', 0)
    
            col1, col2 = st.columns(2)
    
            with col1:
                st.metric("Total de Medidas", total_measures)
    
            with col2:
                display_metric_with_threshold(
                    "Medidas Complejas",
                    complex_measures,
                    thresholds.get('dax_measures_complex')
                )
    
            measures_by_table = metrics.get('measures_by_table', {})
    
            if measures_by_table:
                st.markdown("**Medidas por Tabla:**")
    
                # Crear DataFrame para mejor visualización
                measure_data = []
                for table, measures in measures_by_table.items():
                    if isinstance(measures, list):
                        count = len(measures)
                        measure_names = ', '.join(measures[:3])
                        if len(measures) > 3:
                            measure_names += f" ... (+{len(measures)-3} más)"
                    else:
                        count = measures
                        measure_names = f"{count} medidas"
    
                    measure_data.append({
                        'Tabla': table,
                        'Cantidad': count,
                        'Medidas': measure_names
                    })
    
                df = pd.DataFrame(measure_data).sort_values('Cantidad', ascending=False)
                st.dataframe(df, width="stretch", hide_index=True)
    
        with tab3:
            st.markdown("#### Relaciones del Modelo")
    
            total_rels = metrics.get('total_relationships', 0)
            bidir_rels = metrics.get('bidirectional_relationships', 0)
    
            col1, col2 = st.columns(2)
    
            with col1:
                display_metric_with_threshold(
                    "Total de Relaciones",
                    total_rels,
                    thresholds.get('relationships')
                )
    
            with col2:
                display_metric_with_threshold(
                    "Relaciones Bidireccionales",
                    bidir_rels,
                    thresholds.get('bidirectional_relationships')
                )
    
            # Mostrar relaciones bidireccionales si existen
            bidir_list = metrics.get('bidirectional_relationships_list', [])
            if bidir_list:
                st.warning("⚠️ **Relaciones Bidireccionales Encontradas:**")
                for rel in bidir_list:
                    st.write(f"- `{rel.get('from', 'Unknown')}` ↔️ `{rel.get('to', 'Unknown')}`")
                st.info("💡 Considera usar `CROSSFILTER()` en medidas específicas en lugar de relaciones bidireccionales permanentes.")
    
        with tab4:
            st.markdown("#### Visualizaciones y Páginas")
    
            col1, col2, col3 = st.columns(3)
    
            with col1:
                display_metric_with_threshold(
                    "Páginas Totales",
                    metrics.get('total_pages', 0),
                    thresholds.get('total_pages')
                )
    
            with col2:
                st.metric("Visuales Totales", metrics.get('total_visuals', 0))
    
            with col3:
                avg_visuals = metrics.get('avg_visuals_per_page', 0)
                display_metric_with_threshold(
                    "Promedio Visuales/Página",
                    round(avg_visuals, 1),
                    thresholds.get('visualizations_per_page')
                )
    
            st.markdown("---")
    
            # Métricas adicionales con thresholds
            col4, col5, col6 = st.columns(3)
    
            with col4:
                display_metric_with_threshold(
                    "Custom Visuals",
                    metrics.get('custom_visuals_count', 0),
                    thresholds.get('custom_visuals')
                )
    
            with col5:
                # Formatear explícitamente a 2 decimales
                embedded_mb = metrics.get('embedded_images_mb', 0)
                display_metric_with_threshold(
                    "Imágenes Embebidas (MB)",
                    float(f"{embedded_mb:.2f}") if embedded_mb else 0,
                    thresholds.get('embedded_images_mb')
                )
    
            with col6:
                avg_filters = metrics.get('avg_filters_per_page', 0)
                max_filters = metrics.get('max_filters_per_page', 0)
                if avg_filters or max_filters:
                    st.markdown("**Filtros por Página**")
                    st.metric("Promedio", round(avg_filters, 1))
                    st.caption(f"Máximo: {max_filters} filtros")
                    if max_filters > 8:
                        st.caption("⚠️ Hay páginas con muchos filtros")
                    elif avg_filters > 5:
                        st.caption("⚠️ Promedio alto")
    
            # Tipos de visuales
            visual_types = metrics.get('visual_types', {})
            if visual_types:
                st.markdown("**Distribución de Tipos de Visuales:**")
    
                visual_df = pd.DataFrame([
                    {'Tipo': k, 'Cantidad': v}
                    for k, v in sorted(visual_types.items(), key=lambda x: x[1], reverse=True)
                ])
    
                st.dataframe(visual_df, width="stretch", hide_index=True)
    
    
    def display_recommendations(recommendations):
        """Muestra las recomendaciones mejoradas"""
        if not recommendations:
            st.success("✅ No hay recomendaciones. El reporte cumple con todas las mejores prácticas.")
            return
    
        # Categorizar recomendaciones
        critical = [r for r in recommendations if r.get('severity') == 'critical']
        warnings = [r for r in recommendations if r.get('severity') == 'warning']
        info = [r for r in recommendations if r.get('severity') == 'info']
    
        st.warning(f"⚠️ Se encontraron {len(recommendations)} recomendaciones de mejora")
    
        # Mostrar resumen
        col1, col2, col3 = st.columns(3)
        col1.metric("🔴 Críticas", len(critical))
        col2.metric("🟡 Advertencias", len(warnings))
        col3.metric("ℹ️ Informativas", len(info))
    
        st.markdown("---")
    
        # Críticas
        if critical:
            st.markdown("### 🔴 Recomendaciones Críticas")
            st.info("Las recomendaciones críticas requieren atención inmediata ya que impactan significativamente el rendimiento o la usabilidad.")
    
            for rec in critical:
                with st.expander(f"🔴 {rec['metric'].replace('_', ' ').title()}", expanded=True):
                    # Mensaje principal
                    st.markdown(f"**{rec['message']}**")
                    st.markdown("---")
    
                    # Comparativa visual
                    col1, col2, col3 = st.columns([1, 1, 1])
    
                    with col1:
                        st.markdown("**📊 Valor Actual**")
                        current_val = str(rec['current_value'])
                        # Usar tamaño de fuente más pequeño para todos los valores
                        st.markdown(f"<div style='background-color: rgba(239, 68, 68, 0.1); padding: 0.75rem; border-radius: 8px; border-left: 3px solid #EF4444;'><p style='color: #EF4444; margin: 0; font-size: 0.9rem; line-height: 1.4;'>{current_val}</p></div>", unsafe_allow_html=True)
    
                    with col2:
                        st.markdown("**🎯 Objetivo**")
                        target_val = str(rec['target_value'])
                        # Usar tamaño de fuente más pequeño para todos los valores
                        st.markdown(f"<div style='background-color: rgba(16, 185, 129, 0.1); padding: 0.75rem; border-radius: 8px; border-left: 3px solid #10B981;'><p style='color: #10B981; margin: 0; font-size: 0.9rem; line-height: 1.4;'>{target_val}</p></div>", unsafe_allow_html=True)
    
                    with col3:
                        st.markdown("**💥 Impacto**")
                        st.markdown("<div style='background-color: rgba(245, 158, 11, 0.1); padding: 0.75rem; border-radius: 8px; border-left: 3px solid #F59E0B;'><p style='color: #F59E0B; margin: 0; font-size: 0.9rem; font-weight: 600;'>Alto</p></div>", unsafe_allow_html=True)
    
        # Advertencias
        if warnings:
            st.markdown("### 🟡 Advertencias")
            st.info("Las advertencias indican áreas de mejora que pueden afectar el rendimiento o mantenibilidad.")
    
            for rec in warnings:
                with st.expander(f"🟡 {rec['metric'].replace('_', ' ').title()}"):
                    # Mensaje principal
                    st.markdown(f"**{rec['message']}**")
                    st.markdown("---")
    
                    # Comparativa visual
                    col1, col2, col3 = st.columns([1, 1, 1])
    
                    with col1:
                        st.markdown("**📊 Valor Actual**")
                        current_val = str(rec['current_value'])
                        # Usar tamaño de fuente más pequeño
                        st.markdown(f"<div style='background-color: rgba(245, 158, 11, 0.1); padding: 0.75rem; border-radius: 8px; border-left: 3px solid #F59E0B;'><p style='color: #F59E0B; margin: 0; font-size: 0.9rem; line-height: 1.4;'>{current_val}</p></div>", unsafe_allow_html=True)
    
                    with col2:
                        st.markdown("**🎯 Objetivo**")
                        target_val = str(rec['target_value'])
                        # Usar tamaño de fuente más pequeño
                        st.markdown(f"<div style='background-color: rgba(16, 185, 129, 0.1); padding: 0.75rem; border-radius: 8px; border-left: 3px solid #10B981;'><p style='color: #10B981; margin: 0; font-size: 0.9rem; line-height: 1.4;'>{target_val}</p></div>", unsafe_allow_html=True)
    
                    with col3:
                        st.markdown("**💥 Impacto**")
                        st.markdown("<div style='background-color: rgba(59, 130, 246, 0.1); padding: 0.75rem; border-radius: 8px; border-left: 3px solid #3B82F6;'><p style='color: #3B82F6; margin: 0; font-size: 0.9rem; font-weight: 600;'>Medio</p></div>", unsafe_allow_html=True)
    
        # Informativas
        if info:
            st.markdown("### ℹ️ Información Adicional")
            st.info("Información adicional para optimizar el reporte.")
    
            for rec in info:
                with st.expander(f"ℹ️ {rec['metric'].replace('_', ' ').title()}"):
                    # Mensaje principal
                    st.markdown(f"**{rec['message']}**")
                    st.markdown("---")
    
                    # Comparativa visual
                    col1, col2 = st.columns(2)
    
                    with col1:
                        st.markdown(f"**📊 Valor actual:** `{rec['current_value']}`")
    
                    with col2:
                        st.markdown(f"**🎯 Valor objetivo:** `{rec['target_value']}`")
    
    
    def main():
        # Header
        render_app_header(
            "Power BI Analyzer",
            "Análisis completo de proyectos PBIP",
            "1.1"
        )

        st.markdown("---")

        # PBIP input section
        st.info("📁 **Estructura de Archivos PBIP y Cómo Analizarlos**")

        with st.expander("ℹ️ Entender la estructura PBIP (clic para ver)", expanded=False):
                st.markdown("""
                ### 🗂️ ¿Qué es un proyecto PBIP?
    
                Cuando guardas un reporte como **Power BI Project (.pbip)**, Power BI Desktop crea:
    
                ```
                📁 MiCarpeta/
                ├── 📄 MiReporte.pbip ← ¡COPIA LA RUTA DE ESTE ARCHIVO!
                ├── 📁 MiReporte.Report/ (carpeta con visualizaciones)
                └── 📁 MiReporte.SemanticModel/ (carpeta con el modelo de datos)
                ```
    
                ### ✅ Cómo usar este analizador
    
                **🎯 Método Recomendado (COPIAR ARCHIVO .pbip):**
    
                1. Abre el Explorador de Windows
                2. Busca el archivo con ícono de Power BI que termina en **`.pbip`**
                3. Click derecho → **"Copiar como ruta de acceso"**
                4. Pega en el campo de arriba
    
                **Alternativa:** También puedes copiar la ruta de las carpetas `.Report` o `.SemanticModel`
    
                ### 📝 Importante
                - El archivo `.pbip` debe estar en la **misma carpeta** que `.Report` y `.SemanticModel`
                - Las comillas que agrega Windows automáticamente se eliminarán
                - El analizador detectará todas las carpetas del proyecto automáticamente
                """)

        # PBIP File Selection - Cloud-ready (ZIP upload)
        from shared.pbip_loader import PBIPLoader

        pbip_storage = "/home/cdsw/pbip_projects"
        loader = PBIPLoader(storage_path=pbip_storage)
        file_to_analyze = loader.render_uploader(key="analyzer_pbip_uploader")

        if not file_to_analyze:
            st.stop()

        # Warning about file naming consistency
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(245,158,11,0.08) 0%, rgba(245,158,11,0.02) 100%);
                    border-left: 3px solid #F59E0B; padding: 0.6rem 1rem; border-radius: 0 6px 6px 0;
                    margin: 0.5rem 0; font-size: 0.85rem; color: #78350F;">
            ⚠️ <strong>Mantén el mismo nombre del archivo</strong> entre analisis para que el Usage Dashboard pueda comparar el score antes/despues.
        </div>
        """, unsafe_allow_html=True)
    
        if file_to_analyze:
            try:
                # Crear placeholder para el spinner
                loading_placeholder = st.empty()
    
                # FASE 1: Mostrar spinner de carga animado YPF
                with loading_placeholder.container():
                    st.markdown("""
                        <div class="ypf-loader-container">
                            <div class="ypf-loader"></div>
                            <p class="ypf-loader-text">⚙️ Analizando el reporte Power BI...</p>
                        </div>
                    """, unsafe_allow_html=True)
    
                # ========================================
                # LOGGING: Registrar inicio de análisis
                # ========================================
                analysis_start = time.time()

                # Construir config path correcto
                config_path = Path(__file__).parent.parent / "config" / "analyzer_thresholds.yaml"

                # Realizar análisis con config_path
                result = analyze_powerbi_file(file_to_analyze, config_path=str(config_path))
    
                # ========================================
                # LOGGING: Registrar análisis completado
                # ========================================
                analysis_duration = time.time() - analysis_start
    
                if LOGGING_ENABLED and usage_logger:
                    try:
                        filename = Path(file_to_analyze).name
                        file_size_mb = 0
                        ftype = 'pbip'

                        # Log event con el logger de la suite
                        usage_logger.log_event('pbi_analysis_completed', {
                            'filename': filename,
                            'file_size_mb': file_size_mb,
                            'file_type': ftype,
                            'duration_seconds': analysis_duration,
                            'score': result.get('score'),
                            'recommendations_count': len(result.get('recommendations', []))
                        })
                    except Exception as e:
                        print(f"⚠️ Error al registrar análisis: {e}")
    
                # FASE 2: Mostrar animación de éxito
                loading_placeholder.empty()
                success_placeholder = st.empty()
    
                with success_placeholder.container():
                    st.markdown("""
                        <div style='background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
                                    padding: 1.5rem;
                                    border-radius: 12px;
                                    border: 2px solid #10B981;
                                    text-align: center;
                                    animation: slideIn 0.5s ease-out;'>
                            <p style='color: #10B981; margin: 0; font-size: 1.2rem; font-weight: 700;'>
                                ✅ Reporte analizado con éxito
                            </p>
                        </div>
                        <style>
                            @keyframes slideIn {
                                from {
                                    opacity: 0;
                                    transform: translateY(-20px);
                                }
                                to {
                                    opacity: 1;
                                    transform: translateY(0);
                                }
                            }
                        </style>
                    """, unsafe_allow_html=True)
    
                # Pequeño delay para que se vea el mensaje de éxito
                time.sleep(1.5)
    
                # Limpiar y continuar
                success_placeholder.empty()
    
                # Tabs para organizar la información
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "📈 Overview",
                    "📊 Métricas Detalladas",
                    "💡 Recomendaciones",
                    "⚙️ Configuración",
                    "📄 Exportar"
                ])
    
                with tab1:
                    # Verificar si el análisis del modelo está disponible
                    metrics = result['metrics']
                    model_available = metrics.get('model_analysis_available', True)
    
                    # Mostrar alerta si el modelo no está disponible
                    if not model_available:
                        st.warning("⚠️ **Análisis del Modelo No Disponible**")
                        st.info(metrics.get('model_analysis_note', 'Para análisis completo, use formato PBIP'))
                        st.markdown("---")
    
                    # Score principal
                    col1, col2 = st.columns([1, 2])
    
                    with col1:
                        st.plotly_chart(
                            create_score_gauge(result['score']),
                            width="stretch"
                        )
                        score_label = get_score_label(result['score'])
                        st.markdown(f"### {score_label}")
    
                    with col2:
                        st.markdown("### Resumen Ejecutivo")
    
                        # FIX v1.1: Mostrar solo métricas disponibles
                        first_row_metrics = []
    
                        # Páginas (siempre disponible)
                        first_row_metrics.append(('Páginas', safe_metric_value(metrics.get('total_pages'))))
    
                        # Visualizaciones (siempre disponible)
                        first_row_metrics.append(('Visualizaciones', safe_metric_value(metrics.get('total_visuals'))))
    
                        # Medidas DAX (solo si disponible)
                        if metrics.get('total_measures') is not None:
                            first_row_metrics.append(('Medidas DAX', safe_metric_value(metrics.get('total_measures'))))
    
                        # Tablas (solo si disponible)
                        if metrics.get('total_tables') is not None:
                            first_row_metrics.append(('Tablas', safe_metric_value(metrics.get('total_tables'))))
    
                        # Crear columnas dinámicamente
                        cols = st.columns(len(first_row_metrics))
                        for idx, (label, value) in enumerate(first_row_metrics):
                            with cols[idx]:
                                st.metric(label, value)
    
                        st.markdown("---")
    
                        # FIX v1.1: Mostrar métricas solo si están disponibles
                        available_metrics = []
    
                        # Relaciones
                        if metrics.get('total_relationships') is not None:
                            available_metrics.append(('Relaciones', safe_metric_value(metrics.get('total_relationships')), None))
    
                        # Relaciones Bidireccionales
                        bidir = metrics.get('bidirectional_relationships')
                        if bidir is not None:
                            available_metrics.append(('Rel. Bidireccional', bidir, "⚠️" if bidir > 0 else "✓"))
    
                            # Si hay relaciones bidireccionales, mostrar detalle
                            if bidir > 0:
                                bidir_list = metrics.get('bidirectional_relationships_list', [])
                                if bidir_list:
                                    st.markdown("---")
                                    st.warning(f"⚠️ **{bidir} Relaciones Bidireccionales Detectadas:**")
                                    for rel in bidir_list[:5]:  # Mostrar solo primeras 5 en Overview
                                        st.caption(f"  • {rel.get('from', 'Unknown')} ↔️ {rel.get('to', 'Unknown')}")
                                    if len(bidir_list) > 5:
                                        st.caption(f"  ... y {len(bidir_list) - 5} más (ver en Métricas Detalladas)")
                                    st.info("💡 Considera usar `CROSSFILTER()` en medidas DAX en vez de relaciones bidireccionales permanentes.")
    
                        # Custom Visuals (siempre mostrar)
                        available_metrics.append(('Custom Visuals', safe_metric_value(metrics.get('custom_visuals_count')), None))
    
                        # Tamaño del modelo CON INDICACIÓN DE MEASURE KILLER
                        size = metrics.get('model_size_mb')
                        if size is not None:
                            # Verificar si necesita measure killer (threshold: 250 MB)
                            size_indicator = None
                            if size > 250:
                                size_indicator = "🔴 Measure Killer recomendado"
                            available_metrics.append(('Tamaño (MB)', f"{size:.0f}", size_indicator))
    
                        # Crear columnas dinámicamente basado en métricas disponibles
                        if len(available_metrics) > 0:
                            cols = st.columns(len(available_metrics))
                            for idx, (label, value, delta) in enumerate(available_metrics):
                                with cols[idx]:
                                    if delta:
                                        st.metric(label, value, delta=delta)
                                    else:
                                        st.metric(label, value)

                    # Breakdown por dimensión de calidad (fila full-width bajo el gauge + resumen)
                    st.markdown("---")
                    cat_scores = metrics.get('category_scores')
                    if cat_scores:
                        render_category_breakdown(cat_scores)

                    st.markdown("---")

                    # FIX v1.1: Información adicional - solo si está disponible
                    additional_info = []
    
                    # Auto Date/Time
                    auto_dt = metrics.get('auto_date_time_enabled', 'Desconocido')
                    if auto_dt != 'No disponible' and auto_dt != 'Desconocido':
                        if auto_dt == 'Sí':
                            additional_info.append(('warning', f"⚠️ Auto Date/Time: **Activado**"))
                        else:
                            additional_info.append(('success', f"✅ Auto Date/Time: **Desactivado**"))
    
                    # Columnas Calculadas
                    calc_cols = metrics.get('calculated_columns')
                    if calc_cols is not None:
                        if calc_cols > 10:
                            additional_info.append(('warning', f"⚠️ Columnas Calculadas: **{calc_cols}**"))
                        else:
                            additional_info.append(('info', f"ℹ️ Columnas Calculadas: **{calc_cols}**"))
    
                    # Mostrar información adicional si hay
                    if additional_info:
                        if len(additional_info) == 1:
                            # Solo una métrica, usar ancho completo
                            info_type, info_msg = additional_info[0]
                            if info_type == 'warning':
                                st.warning(info_msg)
                            elif info_type == 'success':
                                st.success(info_msg)
                            else:
                                st.info(info_msg)
                        else:
                            # Múltiples métricas, usar columnas
                            cols = st.columns(len(additional_info))
                            for idx, (info_type, info_msg) in enumerate(additional_info):
                                with cols[idx]:
                                    if info_type == 'warning':
                                        st.warning(info_msg)
                                    elif info_type == 'success':
                                        st.success(info_msg)
                                    else:
                                        st.info(info_msg)
    
                    # ===== NUEVA SECCIÓN: MÉTRICAS DE DISEÑO (v1.1) =====
                    # Esta sección muestra información de diseño que SÍ está disponible en archivos PBIX
                    st.markdown("---")
                    st.markdown("### 🎨 Análisis de Diseño del Reporte")
    
                    # Crear sección expandible con las métricas de diseño
                    with st.expander("📊 Ver métricas detalladas de diseño", expanded=not model_available):
                        # Recomendaciones rápidas antes de las métricas
                        slicers = metrics.get('slicers_count', 0)
                        max_visuals = metrics.get('max_visuals_per_page', 0)
                        embedded_size = metrics.get('embedded_images_mb', 0)
                        bookmarks = metrics.get('bookmarks_count', 0)
                        buttons = metrics.get('buttons_count', 0)
                        total_pages = metrics.get('total_pages', 0)
    
                        # Generar recomendaciones rápidas
                        quick_tips = []
                        if slicers > 15:
                            quick_tips.append("🔴 **Reducir slicers**: Tienes demasiados filtros que confunden al usuario. Consolida o usa sync slicers.")
                        if max_visuals > 20:
                            quick_tips.append("🔴 **Dividir páginas sobrecargadas**: Algunas páginas tienen muchos visuales y afectarán el rendimiento.")
                        if embedded_size > 5:
                            quick_tips.append(f"⚠️ **Optimizar imágenes**: {embedded_size:.2f} MB de imágenes embebidas. Comprímelas o usa referencias externas.")
                        if total_pages > 5 and bookmarks == 0 and buttons == 0:
                            quick_tips.append("💡 **Mejorar navegación**: Añade bookmarks o botones para facilitar la navegación entre páginas.")
                        if not metrics.get('has_custom_theme', False) and total_pages > 1:
                            quick_tips.append("💡 **Crear tema personalizado**: Un tema corporativo mejorará la consistencia visual.")
    
                        if quick_tips:
                            st.markdown("#### 💡 Recomendaciones Rápidas - Dónde Poner el Foco")
                            for tip in quick_tips:
                                st.markdown(tip)
                            st.markdown("---")
    
                        # Primera fila: Elementos interactivos CON INDICADORES DE ESTADO
                        st.markdown("#### 🎯 Elementos Interactivos")
                        col1, col2, col3, col4 = st.columns(4)
    
                        with col1:
                            # Slicers con gradiente de color
                            if slicers > 25:
                                st.markdown("🔴 **Slicers**")
                                st.metric("Slicers", slicers, help="Segmentaciones para filtrar datos", label_visibility="collapsed")
                                st.caption("🔴 Excesivo - Consolidar")
                            elif slicers > 15:
                                st.markdown("⚠️ **Slicers**")
                                st.metric("Slicers", slicers, help="Segmentaciones para filtrar datos", label_visibility="collapsed")
                                st.caption("⚠️ Alto - Revisar")
                            elif slicers > 10:
                                st.markdown("📊 **Slicers**")
                                st.metric("Slicers", slicers, help="Segmentaciones para filtrar datos", label_visibility="collapsed")
                                st.caption("✓ Moderado")
                            else:
                                st.markdown("✅ **Slicers**")
                                st.metric("Slicers", slicers, help="Segmentaciones para filtrar datos", label_visibility="collapsed")
                                st.caption("✅ Óptimo")
    
                        with col2:
                            st.markdown("**Botones**")
                            st.metric("Botones", buttons, help="Botones de acción y navegación", label_visibility="collapsed")
                            if buttons > 0:
                                st.caption("✓ Navegación interactiva")
                            else:
                                st.caption("Sin botones")
    
                        with col3:
                            st.markdown("**Bookmarks**")
                            st.metric("Bookmarks", bookmarks, help="Marcadores guardados", label_visibility="collapsed")
                            if bookmarks > 0:
                                st.caption("✓ Storytelling habilitado")
                            elif total_pages > 5:
                                st.caption("💡 Considera añadir")
                            else:
                                st.caption("Sin bookmarks")
    
                        with col4:
                            st.markdown("**Filtros Reporte**")
                            report_filters = metrics.get('report_level_filters', 0)
                            st.metric("Filtros Reporte", report_filters,
                                     help="Filtros a nivel de reporte: Se aplican a TODAS las páginas del reporte automáticamente (globales)",
                                     label_visibility="collapsed")
                            if report_filters > 3:
                                st.caption("⚠️ Muchos filtros globales")
                            elif report_filters == 0:
                                st.caption("ℹ️ Sin filtros globales")
                            else:
                                st.caption("✓ Nivel razonable")
    
                        st.markdown("---")
    
                        # Segunda fila: Elementos visuales
                        st.markdown("#### 📐 Elementos Visuales")
                        col1, col2, col3, col4 = st.columns(4)
    
                        with col1:
                            shapes = metrics.get('shapes_count', 0)
                            st.metric("Formas", shapes, help="Rectángulos, líneas, círculos")
                            if shapes > 50:
                                st.caption("⚠️ Muchas formas decorativas")
    
                        with col2:
                            textboxes = metrics.get('textboxes_count', 0)
                            st.metric("Cuadros Texto", textboxes, help="Textos y títulos")
    
                        with col3:
                            images = metrics.get('images_in_visuals_count', 0)
                            st.metric("Imágenes", images, help="Imágenes como visuales")
    
                        with col4:
                            tables = metrics.get('tables_count', 0)
                            st.metric("Tablas/Matrices", tables, help="Tablas y matrices de datos")
    
                        st.markdown("---")
    
                        # Tercera fila: Configuración de páginas
                        st.markdown("#### 📄 Configuración de Páginas")
                        col1, col2, col3 = st.columns(3)
    
                        with col1:
                            hidden = metrics.get('hidden_pages_count', 0)
                            st.metric("Páginas Ocultas", hidden, help="Páginas no visibles para usuarios")
                            if hidden > 0:
                                st.caption("ℹ️ Usadas para navegación")
    
                        with col2:
                            tooltips = metrics.get('tooltip_pages_count', 0)
                            st.metric("Páginas Tooltip", tooltips, help="Tooltips personalizados")
                            if tooltips > 0:
                                st.caption("✓ UX avanzada")
    
                        with col3:
                            embedded_imgs = metrics.get('embedded_images_count', 0)
                            # Redondear a 2 decimales
                            if embedded_size > 10:
                                st.markdown("🔴 **Imágenes Embebidas**")
                                st.metric("Imágenes Embebidas", embedded_imgs, help="Recursos estáticos embebidos", label_visibility="collapsed")
                                st.caption(f"🔴 {embedded_size:.2f} MB - Optimizar")
                            elif embedded_size > 5:
                                st.markdown("⚠️ **Imágenes Embebidas**")
                                st.metric("Imágenes Embebidas", embedded_imgs, help="Recursos estáticos embebidos", label_visibility="collapsed")
                                st.caption(f"⚠️ {embedded_size:.2f} MB - Revisar")
                            else:
                                st.markdown("**Imágenes Embebidas**")
                                st.metric("Imágenes Embebidas", embedded_imgs, help="Recursos estáticos embebidos", label_visibility="collapsed")
                                if embedded_size > 0:
                                    st.caption(f"✓ {embedded_size:.2f} MB")
    
                        # Información del tema
                        st.markdown("---")
                        st.markdown("#### 🎨 Configuración de Tema")
    
                        col1, col2 = st.columns(2)
    
                        with col1:
                            has_theme = metrics.get('has_custom_theme', False)
                            theme_name = metrics.get('theme_name', 'Desconocido')
                            if has_theme:
                                st.success(f"✅ Tema personalizado: **{theme_name}**")
                            else:
                                st.info(f"💡 Tema predeterminado - Considera crear uno corporativo")
    
                        with col2:
                            report_config = metrics.get('report_config', {})
                            default_page = report_config.get('default_page', 'N/A')
                            st.info(f"📄 Página inicial: **{default_page}**")
    
                        # Detalles de páginas - MEJORADO sin columna "Tipo" confusa
                        pages_detail = metrics.get('pages_detail', [])
                        if pages_detail:
                            st.markdown("---")
                            st.markdown("#### 📄 Detalles por Página")
    
                            df_pages = pd.DataFrame([{
                                'Página': p['name'],
                                'Visuales': p['visuals_count'],
                                'Filtros': p['filters_count'],
                                'Estado': '🔴 Crítico' if p['visuals_count'] > 20 else ('⚠️ Alto' if p['visuals_count'] > 15 else '✅ Óptimo'),
                                'Especial': 'Tooltip' if p.get('tooltip') else ('Oculta' if p.get('hidden') else '-')
                            } for p in pages_detail])
    
                            st.dataframe(df_pages, width="stretch", hide_index=True)
    
                            # Explicación clara de criterios
                            st.info("""
                            **📊 Criterios de Estado:**
                            - ✅ **Óptimo**: ≤15 visuales por página - Carga rápida, buena experiencia de usuario
                            - ⚠️ **Alto**: 16-20 visuales - Aceptable pero puede afectar rendimiento
                            - 🔴 **Crítico**: >20 visuales - Impacta significativamente el rendimiento. Divide la página o usa drill-through/tooltips
    
                            **🏷️ Tipos Especiales:**
                            - **Tooltip**: Páginas que se muestran al pasar el mouse sobre visuales
                            - **Oculta**: Páginas no visibles para usuarios finales (ej: páginas de navegación)
                            """)
    
                        # Bookmarks detail
                        bookmarks_detail = metrics.get('bookmarks_detail', [])
                        if bookmarks_detail:
                            with st.expander("🔖 Ver detalle de bookmarks"):
                                for bm in bookmarks_detail:
                                    st.write(f"- **{bm['name']}** → {bm['page']}")

                    # ===== NUEVA SECCIÓN: STORAGE MODE ANALYSIS (v2.0) =====
                    if model_available:
                        st.markdown("---")
                        st.markdown("### 🔗 Storage Mode & DirectQuery")

                        tables_by_mode = metrics.get('tables_by_mode', {})
                        storage_type = metrics.get('storage_mode_type', 'import')
                        dq_issues = metrics.get('directquery_issues', [])
                        dq_detail = metrics.get('directquery_tables_detail', [])
                        folding_warnings = metrics.get('query_folding_warnings', [])

                        if tables_by_mode:
                            total_tables_sm = sum(tables_by_mode.values())
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                n_import = tables_by_mode.get('import', 0)
                                pct_import = (n_import / total_tables_sm * 100) if total_tables_sm else 0
                                st.metric("📦 Import", n_import)
                                st.caption(f"{pct_import:.0f}% del modelo")
                            with col2:
                                n_dq = tables_by_mode.get('directQuery', 0)
                                pct_dq = (n_dq / total_tables_sm * 100) if total_tables_sm else 0
                                st.metric("🔗 DirectQuery", n_dq)
                                st.caption(f"{pct_dq:.0f}% del modelo")
                            with col3:
                                n_dual = tables_by_mode.get('dual', 0)
                                pct_dual = (n_dual / total_tables_sm * 100) if total_tables_sm else 0
                                st.metric("🔄 Dual", n_dual)
                                st.caption(f"{pct_dual:.0f}% del modelo")

                            # Arquitectura del modelo
                            st.markdown("---")
                            type_labels = {
                                "import": ("📦 Import puro", "#107C10"),
                                "directQuery": ("🔗 DirectQuery puro", "#F59E0B"),
                                "composite": ("🔀 Composite Model", "#3B82F6"),
                            }
                            label, color = type_labels.get(storage_type, ("? Desconocido", "#5A6478"))
                            st.markdown(f"**Arquitectura del modelo:** {label}")

                            # Issues críticos
                            critical = [i for i in dq_issues if i.get('severity') == 'critical']
                            warnings = [i for i in dq_issues if i.get('severity') == 'warning']

                            if critical:
                                st.error(f"🔴 {len(critical)} error(es) crítico(s) en tablas DirectQuery")
                                with st.expander("Ver issues críticos"):
                                    for i in critical[:10]:
                                        col_str = f" · `{i['column']}`" if i.get('column') else ""
                                        st.markdown(f"**{i['issue']}** — `{i['table']}`{col_str}")
                                        st.caption(i.get('detail', ''))

                            if warnings:
                                st.warning(f"🟡 {len(warnings)} función(es) DAX con soporte limitado en DirectQuery")

                            if folding_warnings:
                                st.warning(f"⚠️ {len(folding_warnings)} anti-pattern(s) en M code que rompen query folding")

                            # Tablas DirectQuery detail
                            if dq_detail:
                                with st.expander(f"🔗 Ver {len(dq_detail)} tablas DirectQuery/Dual"):
                                    for t in dq_detail[:15]:
                                        st.markdown(f"**{t['name']}** — mode: `{t['mode']}`")
                                        if t.get('n_calculated_columns', 0) > 0:
                                            st.caption(f"❌ {t['n_calculated_columns']} columna(s) calculada(s) — ERROR CRÍTICO")
                                        if t.get('source_snippet'):
                                            st.code(t['source_snippet'][:150] + "..." if len(t['source_snippet']) > 150 else t['source_snippet'], language='powerquery')

                            # Todo OK
                            if not dq_issues and not folding_warnings and not dq_detail:
                                st.success("✓ Storage mode saludable — modelo Import puro sin issues de DirectQuery")
                        else:
                            st.info("No se detectaron tablas con storage mode information.")

                with tab2:
                    st.markdown("## Métricas Detalladas")
    
                    # ===== TAMAÑO DEL MODELO ARRIBA DE TODO (MOVIDO) =====
                    model_available = metrics.get('model_analysis_available', True)
                    if model_available:
                        st.markdown("### 💾 Tamaño del Modelo")
    
                        size_mb = metrics.get('model_size_mb', 0)
                        if size_mb is not None and size_mb > 0:
                            col1, col2 = st.columns(2)
    
                            with col1:
                                st.metric("Tamaño Total", f"{size_mb:.1f} MB")
    
                                # Indicador de Measure Killer basado en threshold
                                if size_mb > 250:
                                    st.error("🔴 **Modelo muy grande - Measure Killer RECOMENDADO**")
                                    st.caption("El modelo supera los 250 MB. Usa Measure Killer para identificar y eliminar medidas no utilizadas.")
                                elif size_mb > 100:
                                    st.warning("⚠️ **Modelo grande - Considerar Measure Killer**")
                                    st.caption("El modelo es grande. Revisa si hay medidas no utilizadas.")
                                else:
                                    st.success("✅ **Tamaño aceptable**")
                                    st.caption("El modelo está dentro de límites razonables.")
    
                            with col2:
                                images_mb = metrics.get('embedded_images_mb', 0)
                                st.metric("Imágenes Embebidas", f"{images_mb:.2f} MB")
                                if images_mb > 5:
                                    st.caption("⚠️ Considera optimizar")
                                else:
                                    st.caption("✓ Tamaño razonable")
    
                        st.markdown("---")
    
                    # ===== PANEL DE PROBLEMAS CRÍTICOS (NUEVO) =====
                    st.markdown("### 🎯 Áreas de Atención")
    
                    # Filtrar recomendaciones críticas y warnings
                    critical_recs = [r for r in result['recommendations'] if r['severity'] == 'critical']
                    warning_recs = [r for r in result['recommendations'] if r['severity'] == 'warning']
    
                    if critical_recs or warning_recs:
                        # Mostrar en formato de alerta visual
                        if critical_recs:
                            st.error("🔴 **Problemas Críticos que Requieren Atención Inmediata:**")
                            for rec in critical_recs:
                                with st.expander(f"🔴 {rec['metric'].replace('_', ' ').title()}", expanded=True):
                                    st.markdown(f"**{rec['message']}**")
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.metric("Valor Actual", rec['current_value'])
                                    with col2:
                                        st.metric("Objetivo", rec['target_value'])
    
                        if warning_recs:
                            st.warning("⚠️ **Advertencias - Recomendamos Revisar:**")
                            for rec in warning_recs:
                                with st.expander(f"⚠️ {rec['metric'].replace('_', ' ').title()}"):
                                    st.markdown(f"**{rec['message']}**")
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.metric("Valor Actual", rec['current_value'])
                                    with col2:
                                        st.metric("Objetivo", rec['target_value'])
                    else:
                        st.success("✅ **¡Excelente! No se encontraron problemas críticos.**")
                        st.info("El reporte sigue las mejores prácticas de diseño.")
    
                    st.markdown("---")
    
                    # ===== MÉTRICAS DE VISUALIZACIONES (SIMPLIFICADO) =====
                    st.markdown("### 📊 Visualizaciones y Páginas")
    
                    col1, col2, col3 = st.columns(3)
    
                    with col1:
                        st.metric("Total Páginas", metrics.get('total_pages', 0))
                        st.caption(f"Promedio: {metrics.get('avg_visuals_per_page', 0):.1f} visuales/página")
    
                    with col2:
                        st.metric("Total Visuales", metrics.get('total_visuals', 0))
                        max_visuals = metrics.get('max_visuals_per_page', 0)
                        if max_visuals > 15:
                            st.caption(f"⚠️ Máximo: {max_visuals} en una página")
                        else:
                            st.caption(f"✓ Máximo: {max_visuals} en una página")
    
                    with col3:
                        custom = metrics.get('custom_visuals_count', 0)
                        st.metric("Custom Visuals", custom)
                        if custom > 0:
                            st.caption("✓ Usando visuales personalizados")
    
                    # Detalle de páginas
                    pages_detail = metrics.get('pages_detail', [])
                    if pages_detail:
                        st.markdown("#### 📄 Análisis por Página")
    
                        df_pages = pd.DataFrame([{
                            'Página': p['name'],
                            'Visuales': p['visuals_count'],
                            'Filtros': p['filters_count'],
                            'Estado': '🔴 Crítico' if p['visuals_count'] > 20 else ('⚠️ Alto' if p['visuals_count'] > 15 else '✅ Óptimo'),
                            'Tipo': 'Tooltip' if p.get('tooltip') else ('Oculta' if p.get('hidden') else 'Normal')
                        } for p in pages_detail])
    
                        st.dataframe(df_pages, width="stretch", hide_index=True)
    
                        # Explicación clara de criterios
                        st.caption("""
                        **Criterios**: ✅ Óptimo (≤15 visuales) | ⚠️ Alto (16-20) | 🔴 Crítico (>20)
                        - Páginas con >20 visuales afectan significativamente el rendimiento
                        """)
    
                    # Sección de modelo movida arriba - ya no se necesita aquí
                    if not model_available:
                        st.markdown("---")
                        st.info("ℹ️ **Métricas del modelo no disponibles para este archivo.**")
    
                with tab3:
                    st.markdown("## Recomendaciones")
                    display_recommendations(result['recommendations'])
    
                with tab4:
                    st.markdown("## ⚙️ Configuración de Thresholds")
    
                    st.info("Aquí puedes ajustar los umbrales de las métricas (próximamente editable desde la UI)")
    
                    # Mostrar configuración actual
                    config_path = os.path.join(Path(__file__).parent.parent, 'config', 'analyzer_thresholds.yaml')
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
    
                    st.markdown("### Umbrales Actuales")
    
                    thresholds = config.get('thresholds', {})
                    threshold_data = []
    
                    for key, values in thresholds.items():
                        threshold_data.append({
                            'Métrica': key.replace('_', ' ').title(),
                            'Bueno (≤)': values.get('good', 'N/A'),
                            'Advertencia (≤)': values.get('warning', 'N/A'),
                            'Crítico (>)': values.get('critical', 'N/A'),
                        })
    
                    df_thresholds = pd.DataFrame(threshold_data)
                    st.dataframe(df_thresholds, width="stretch", hide_index=True)
    
                with tab5:
                    st.markdown("## Exportar Resultados")
    
                    # Sanitizar nombre del reporte para usar en archivos
                    clean_name = sanitize_filename(result['report_name'])
    
                    # Mostrar JSON siempre disponible para PBIP
                    show_json = True

                    # Initialize session state for export buttons
                    if 'html_generated' not in st.session_state:
                        st.session_state.html_generated = False
                        st.session_state.html_content = None
                        st.session_state.html_filename = None
                    if 'json_generated' not in st.session_state:
                        st.session_state.json_generated = False
                        st.session_state.json_content = None
                        st.session_state.json_filename = None

                    # CSS for success button state
                    st.markdown("""
                    <style>
                    .stDownloadButton > button {
                        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
                        border: 1px solid #10b981 !important;
                        color: white !important;
                        font-weight: 600 !important;
                        transition: all 280ms ease !important;
                    }
                    .stDownloadButton > button:hover {
                        background: linear-gradient(135deg, #047857 0%, #065f46 100%) !important;
                        box-shadow: 0 4px 12px rgba(5,150,105,0.3) !important;
                        transform: translateY(-1px) !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)

                    # Crear columnas para las opciones
                    col1, col2 = st.columns(2)

                    # Opción 1: HTML (siempre disponible)
                    with col1:
                        st.markdown("### 📄 Reporte HTML Interactivo")
                        st.write("Genera un reporte HTML completo con gráficos interactivos.")
                        st.write("**Incluye**: Botón para imprimir o guardar como PDF directamente desde el navegador.")

                        # Example images
                        with st.expander("👁️ Ver ejemplo de reporte HTML"):
                            html_ex1 = Path(__file__).parent.parent / "assets" / "export_html_example_1.jpg"
                            html_ex2 = Path(__file__).parent.parent / "assets" / "export_html_example_2.jpg"
                            if html_ex1.exists():
                                st.image(str(html_ex1), caption="Vista de reporte HTML", use_container_width=True)
                            if html_ex2.exists():
                                st.image(str(html_ex2), caption="Detalles del análisis", use_container_width=True)

                        # Show generate button only if not generated yet
                        if not st.session_state.html_generated:
                            if st.button("🎨 Generar Reporte HTML", key="gen_html", use_container_width=True, type="primary"):
                                with st.spinner("Generando reporte HTML..."):
                                    generator = ReportGenerator()
                                    output_path = os.path.join(
                                        tempfile.gettempdir(),
                                        f"PowerBI_Report_{clean_name}.html"
                                    )
                                    generator.generate_html_report(result, output_path)

                                    # ========================================
                                    # LOGGING: Registrar reporte HTML generado
                                    # ========================================
                                    if LOGGING_ENABLED and usage_logger:
                                        try:
                                            report_size_kb = os.path.getsize(output_path) / 1024
                                            usage_logger.log_event('report_generated', {
                                                'report_format': 'html',
                                                'report_size_kb': report_size_kb
                                            })
                                        except Exception as e:
                                            print(f"⚠️ Error al registrar reporte: {e}")

                                    with open(output_path, 'r', encoding='utf-8') as f:
                                        html_content = f.read()

                                    # Store in session state
                                    st.session_state.html_generated = True
                                    st.session_state.html_content = html_content
                                    st.session_state.html_filename = f"PowerBI_Report_{clean_name}.html"

                                st.success("✅ Reporte HTML generado exitosamente!")
                                st.rerun()

                        # Show download button if generated
                        if st.session_state.html_generated:
                            st.download_button(
                                label="📥 Descargar Reporte HTML",
                                data=st.session_state.html_content,
                                file_name=st.session_state.html_filename,
                                mime="text/html",
                                use_container_width=True,
                                key="download_html"
                            )
                            st.info("💡 **Tip**: Una vez descargado, abre el archivo HTML y usa el botón 'Imprimir/Guardar como PDF' en la esquina superior derecha para generar un PDF.")

                    # Opción 2: JSON (solo para PBIP)
                    if show_json and col2:
                        with col2:
                            st.markdown("### 📊 Datos en Formato JSON")
                            st.write("Exporta todos los datos del análisis en formato JSON.")
                            st.write("**Útil para**: Procesamiento programático o integración con otras herramientas.")

                            # Example image
                            with st.expander("👁️ Ver ejemplo de integración JSON"):
                                json_ex = Path(__file__).parent.parent / "assets" / "export_json_example.jpg"
                                if json_ex.exists():
                                    st.image(str(json_ex), caption="JSON en Power BI - Integración directa", use_container_width=True)
                                st.info("💡 El JSON exportado puede ser importado directamente en Power BI para análisis adicional")

                            # Show generate button only if not generated yet
                            if not st.session_state.json_generated:
                                if st.button("📊 Generar JSON", key="gen_json", use_container_width=True):
                                    json_content = json.dumps(result, indent=2, ensure_ascii=False)

                                    # ========================================
                                    # LOGGING: Registrar reporte JSON generado
                                    # ========================================
                                    if LOGGING_ENABLED and usage_logger:
                                        try:
                                            report_size_kb = len(json_content.encode('utf-8')) / 1024
                                            usage_logger.log_event('report_generated', {
                                                'report_format': 'json',
                                                'report_size_kb': report_size_kb
                                            })
                                        except Exception as e:
                                            print(f"⚠️ Error al registrar reporte: {e}")

                                    # Store in session state
                                    st.session_state.json_generated = True
                                    st.session_state.json_content = json_content
                                    st.session_state.json_filename = f"PowerBI_Report_{clean_name}.json"

                                    st.success("✅ JSON generado exitosamente!")
                                    st.rerun()

                            # Show download button if generated
                            if st.session_state.json_generated:
                                st.download_button(
                                    label="📥 Descargar JSON",
                                    data=st.session_state.json_content,
                                    file_name=st.session_state.json_filename,
                                    mime="application/json",
                                    use_container_width=True,
                                    key="download_json"
                                )
    
                    # Mensaje informativo
                    st.markdown("---")
                    st.markdown("### 📋 Opciones de Exportación")
    
                    if show_json:
                        st.info("""
                        **HTML**: Reporte visual completo con gráficos interactivos y botón para guardar como PDF.
    
                        **JSON**: Datos estructurados para procesamiento automático o integración con otras herramientas.
                        """)
                    else:
                        st.info("""
                        **HTML**: Reporte visual completo con gráficos interactivos.
    
                        **PDF**: Desde el HTML descargado, usa el botón "Imprimir/Guardar como PDF" o la función de impresión de tu navegador (Ctrl+P / Cmd+P).
    
                        💡 **Nota**: La exportación JSON está disponible solo para proyectos PBIP ya que contiene más información del modelo de datos.
                        """)
    
            except Exception as e:
                st.error(f"❌ Error analizando el archivo: {str(e)}")
                st.exception(e)
    
            finally:
                pass

        else:
            # Mostrar instrucciones cuando no hay archivo cargado
            st.markdown("""
                <div style='background: linear-gradient(135deg, rgba(4,81,228,0.05) 0%, rgba(0,0,0,0.02) 100%);
                            padding: 2rem;
                            border-radius: 12px;
                            border-left: 5px solid #0451E4;
                            margin: 2rem 0;'>
                    <h3 style='color: #000000; margin: 0 0 1rem 0;'>
                        📁 Proyecto PBIP
                    </h3>
                    <p style='color: #666; font-size: 1rem; margin: 0;'>
                        👆 Copia y pega la ruta del archivo <strong>.pbip</strong> en el campo de arriba
                    </p>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            ### ¿Cómo funciona?

            1. Copia la ruta completa de tu archivo `.pbip`
            2. Pega la ruta en el campo de arriba (las comillas se eliminan automáticamente)
            3. Espera el análisis automático
            4. Revisa resultados y exporta reportes

            ### Criterios de Evaluación

            La herramienta evalúa tu reporte en base a umbrales definidos para cada métrica:

            - ✅ **Verde**: Cumple con las mejores prácticas
            - ⚠️ **Amarillo**: Aceptable pero mejorable
            - 🔴 **Rojo**: Requiere atención inmediata
            """)

    # Ejecutar la aplicación
    main()

    if __name__ == "__main__":
        main()

"""Storage Mode Advisor — analiza la distribución de storage modes
y emite recomendaciones para modelos Import / DirectQuery / Composite.

No requiere conexión al modelo; trabaja sobre el dict que produce
`tmdl_parser.PBIPTMDLParser.parse()` (cada tabla con `storageMode`
y `partitions`).
"""

from typing import Dict, List, Any


def analyze_storage_modes(tables: List[Dict[str, Any]],
                          estimated_size_mb: float = 0.0) -> Dict[str, Any]:
    """Analiza storage modes de un modelo PBIP.

    Args:
        tables: lista de dicts (output de tmdl_parser); cada uno con
                `name`, `storageMode`, `partitions`, `columns`, `tableType`.
        estimated_size_mb: tamaño estimado del modelo (puede ser burdo en PBIP).

    Returns:
        {
            'distribution': {import, directQuery, dual, unknown},
            'model_type': 'Import' | 'DirectQuery' | 'Composite' | 'Vacío',
            'tables_by_mode': {mode: [table_names]},
            'anti_patterns': [{table, issue, severity, fix}],
            'recommendations': [{title, body, priority}],
        }
    """
    user_tables = [t for t in tables if not t.get('isSystemTable', False)]
    if not user_tables:
        return {
            'distribution': {},
            'model_type': 'Vacío',
            'tables_by_mode': {},
            'anti_patterns': [],
            'recommendations': [],
        }

    distribution: Dict[str, int] = {}
    tables_by_mode: Dict[str, List[str]] = {}
    for t in user_tables:
        mode = _extract_mode(t)
        distribution[mode] = distribution.get(mode, 0) + 1
        tables_by_mode.setdefault(mode, []).append(t.get('name', '?'))

    model_type = _classify_model(distribution)
    anti_patterns = _detect_anti_patterns(user_tables)
    recommendations = _build_recommendations(
        model_type=model_type,
        distribution=distribution,
        size_mb=estimated_size_mb,
        n_tables=len(user_tables),
        anti_patterns=anti_patterns,
    )

    return {
        'distribution': distribution,
        'model_type': model_type,
        'tables_by_mode': tables_by_mode,
        'anti_patterns': anti_patterns,
        'recommendations': recommendations,
    }


def _extract_mode(table: Dict[str, Any]) -> str:
    """Extrae storage mode tolerando ambos shapes: TMDL parseado y BIM JSON.

    Prioridad: `storageMode` directo (TMDL parser) → primera partition.mode
    (BIM o TMDL viejo) → 'unknown'.
    """
    direct = table.get('storageMode')
    if direct:
        return direct
    partitions = table.get('partitions') or []
    if partitions and isinstance(partitions, list):
        mode = partitions[0].get('mode') if isinstance(partitions[0], dict) else None
        if mode:
            return mode
    return 'unknown'


def _classify_model(dist: Dict[str, int]) -> str:
    """Etiqueta el modelo segun su mezcla de modes."""
    modes = {m for m, n in dist.items() if n > 0 and m != 'unknown'}
    if not modes:
        return 'Desconocido'
    if modes == {'import'}:
        return 'Import'
    if modes == {'directQuery'}:
        return 'DirectQuery'
    # Cualquier mezcla import + directQuery + dual = Composite
    if 'directQuery' in modes and ('import' in modes or 'dual' in modes):
        return 'Composite'
    if modes == {'dual'}:
        return 'Composite (Dual)'
    return 'Mixto'


def _detect_anti_patterns(tables: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Detecta anti-patterns específicos por storage mode."""
    issues = []
    for t in tables:
        mode = _extract_mode(t)
        tname = t.get('name', '?')

        # 1) Columnas calculadas en tabla DirectQuery → se evalúan por query
        if mode == 'directQuery':
            calc_cols = [c['name'] for c in t.get('columns', [])
                         if c.get('isCalculated') or c.get('expression')]
            if calc_cols:
                issues.append({
                    'table': tname,
                    'issue': f'Columnas calculadas en tabla DirectQuery: {", ".join(calc_cols[:3])}'
                             f'{"…" if len(calc_cols) > 3 else ""}',
                    'severity': 'warning',
                    'fix': 'Mover la lógica a una vista del origen (SQL) o cambiar la tabla a Import.',
                })

            # 2) DQ con tabla calculada (kind = calculated) → no soportado
            for p in t.get('partitions', []):
                if p.get('kind') == 'calculated':
                    issues.append({
                        'table': tname,
                        'issue': 'Tabla calculada con storage mode DirectQuery (no soportado)',
                        'severity': 'critical',
                        'fix': 'Materializar en el origen o cambiar a Import.',
                    })

        # 3) Mode unknown — usualmente parser no detectó. Diagnóstico, no anti-pattern duro.
        if mode == 'unknown' and t.get('tableType') == 'user':
            issues.append({
                'table': tname,
                'issue': 'No se pudo determinar storage mode (revisar TMDL manualmente)',
                'severity': 'info',
                'fix': 'Abrir la tabla en Power BI Desktop y verificar Storage Mode.',
            })

    return issues


def _build_recommendations(model_type: str,
                           distribution: Dict[str, int],
                           size_mb: float,
                           n_tables: int,
                           anti_patterns: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Genera recomendaciones priorizadas segun el perfil del modelo."""
    recs: List[Dict[str, str]] = []

    n_import = distribution.get('import', 0)
    n_dq = distribution.get('directQuery', 0)
    n_dual = distribution.get('dual', 0)

    # ── Recomendaciones por tipo de modelo ──
    if model_type == 'DirectQuery':
        recs.append({
            'title': 'Modelo 100% DirectQuery',
            'body': 'Todo el modelo consulta el origen en cada query. '
                    'Verificá query folding y considerá migrar dimensiones chicas a Import '
                    '(modelo Composite) para mejorar performance.',
            'priority': 'P1',
        })
        # Pequeño + DQ → probablemente debería ser Import
        if size_mb > 0 and size_mb < 100 and n_tables < 20:
            recs.append({
                'title': 'Modelo chico en DirectQuery — considerá Import',
                'body': f'El modelo es chico ({size_mb:.0f}MB, {n_tables} tablas). '
                        f'Import sería mucho más rápido y simplifica el deployment.',
                'priority': 'P1',
            })

    elif model_type == 'Import':
        # Grande + Import → considerar Composite con aggregations
        if size_mb > 5000 or n_tables > 50:
            recs.append({
                'title': 'Modelo grande en Import — considerá Composite + aggregations',
                'body': f'Modelo grande ({size_mb:.0f}MB, {n_tables} tablas). '
                        f'Evaluá migrar tablas fact a DirectQuery y dejar dimensiones en Import. '
                        f'Usá Aggregation Tables para acelerar consultas frecuentes.',
                'priority': 'P2',
            })

    elif model_type == 'Composite':
        recs.append({
            'title': 'Modelo Composite detectado',
            'body': f'Mezcla de modes: {n_import} Import + {n_dq} DirectQuery'
                    f'{f" + {n_dual} Dual" if n_dual else ""}. '
                    f'Buena arquitectura para modelos grandes — verificá que las dimensiones '
                    f'usadas por tablas DQ estén en modo Dual.',
            'priority': 'P3',
        })

    # ── Recomendaciones basadas en anti-patterns ──
    n_critical = sum(1 for a in anti_patterns if a['severity'] == 'critical')
    n_warning = sum(1 for a in anti_patterns if a['severity'] == 'warning')
    if n_critical:
        recs.append({
            'title': f'{n_critical} anti-pattern(s) crítico(s) en DirectQuery',
            'body': 'Hay configuraciones que pueden fallar en runtime. Revisá la lista abajo.',
            'priority': 'P0',
        })
    if n_warning:
        recs.append({
            'title': f'{n_warning} configuracion(es) que penalizan performance',
            'body': 'Columnas calculadas en tablas DirectQuery hacen que la query se ejecute '
                    'cada vez que el visual refresca. Movelas al origen.',
            'priority': 'P1',
        })

    if not recs:
        recs.append({
            'title': 'Sin recomendaciones',
            'body': f'Modelo {model_type} sin anti-patterns detectados. '
                    f'Recordá revisar query folding si usás DirectQuery.',
            'priority': 'P3',
        })

    return recs

# 🔧 Instrucciones de Migración Manual - YPF BI Monitor Cloud

**Para:** Desarrolladores que necesitan migrar las apps manualmente  
**Tiempo:** 10-15 minutos por app  
**Dificultad:** 🟢 Baja

---

## 🎯 Objetivo

Convertir cada app de YPF BI Monitor para que funcione en Cloudera AI Workbench usando el nuevo sistema de upload de archivos ZIP en lugar de rutas locales.

---

## 📝 Cambios Necesarios por App

### **Antes (Versión Local)**

```python
# apps/powerbi_analyzer.py - ORIGINAL

import streamlit as st
from pathlib import Path
from apps_core.analyzer_core.core import analyze_powerbi_file

def render_app(logger):
    st.title("📊 Power BI Analyzer")
    
    # ❌ PROBLEMA: Solo funciona con rutas locales
    pbip_path = st.text_input(
        "📁 Ruta al archivo .pbip",
        placeholder="C:/Users/usuario/MiReporte/MiReporte.pbip",
        help="Ingresa la ruta completa al archivo .pbip"
    )
    
    # ❌ PROBLEMA: Necesita validar que el archivo existe
    if pbip_path and not Path(pbip_path).exists():
        st.error("❌ Archivo no encontrado. Verifica la ruta.")
        return
    
    if pbip_path:
        if st.button("Analizar"):
            results = analyze_powerbi_file(pbip_path)
            # ... mostrar resultados
```

---

### **Después (Versión Cloud-Ready)**

```python
# apps/powerbi_analyzer.py - CLOUD READY

import streamlit as st
from pathlib import Path
from apps_core.analyzer_core.core import analyze_powerbi_file
from shared.pbip_loader import load_pbip_cloud_ready  # ← 1️⃣ AGREGAR IMPORT

def render_app(logger):
    st.title("📊 Power BI Analyzer")
    
    # ✅ 2️⃣ REEMPLAZAR text_input con load_pbip_cloud_ready
    pbip_path = load_pbip_cloud_ready(
        key="analyzer_upload",        # Único por app
        persistent_storage=True         # Habilitar guardado de proyectos
    )
    
    # ✅ 3️⃣ ELIMINAR validación de path (el loader lo maneja)
    # if pbip_path and not Path(pbip_path).exists():  ← BORRAR ESTO
    #     st.error("...")
    #     return
    
    # ✅ 4️⃣ TODO LO DEMÁS QUEDA IGUAL
    if pbip_path:
        if st.button("Analizar"):
            results = analyze_powerbi_file(pbip_path)
            # ... mostrar resultados
```

---

## 📋 Checklist de Cambios por App

### ✅ Paso 1: Agregar Import

**Ubicación:** Inicio del archivo, después de `import streamlit as st`

```python
from shared.pbip_loader import load_pbip_cloud_ready
```

---

### ✅ Paso 2: Reemplazar text_input

**Buscar:**
```python
pbip_path = st.text_input(
    "📁 Ruta al archivo .pbip",
    ...
)
```

**Reemplazar con:**
```python
pbip_path = load_pbip_cloud_ready(
    key="<app_unique_key>",  # Ver tabla abajo
    persistent_storage=True
)
```

**Keys únicas por app:**

| App | Key Recomendada |
|-----|----------------|
| Power BI Analyzer | `"analyzer_upload"` |
| Documentation Generator | `"docgen_upload"` |
| DAX Optimizer | `"dax_optimizer_upload"` |
| Layout Organizer | `"layout_upload"` |
| BI Bot | `"bibot_upload"` |

---

### ✅ Paso 3: Eliminar Validación de Path

**Buscar y ELIMINAR:**

```python
if pbip_path and not Path(pbip_path).exists():
    st.error("❌ Archivo no encontrado")
    return
```

o

```python
if not pbip_path or not Path(pbip_path).exists():
    st.warning("Por favor ingresa una ruta válida")
    return
```

**¿Por qué?** El nuevo loader ya valida automáticamente y muestra errores apropiados.

---

### ✅ Paso 4: Verificar Lógica de Procesamiento

**Verificar que esta lógica NO cambie:**

```python
if pbip_path:
    # ✅ Esta lógica debe permanecer EXACTAMENTE IGUAL
    results = analyze_powerbi_file(pbip_path)
    
    # ✅ El resto del código de la app NO cambia
    st.json(results)
    # ... etc
```

---

## 🔄 Apps a Migrar

### Lista Completa

| # | App | Archivo | Status | Prioridad |
|---|-----|---------|--------|-----------|
| 1 | Power BI Analyzer | `apps/powerbi_analyzer.py` | ⏳ Pendiente | 🔴 Alta |
| 2 | Documentation Generator | `apps/documentation_generator.py` | ⏳ Pendiente | 🔴 Alta |
| 3 | DAX Optimizer | `apps/dax_optimizer.py` | ⏳ Pendiente | 🟡 Media |
| 4 | Layout Organizer | `apps/layout_organizer.py` | ⏳ Pendiente | 🟡 Media |
| 5 | BI Bot | `apps/bi_bot.py` | ⏳ Pendiente | 🟢 Baja |

**Notas:**
- BI Bot puede tener lógica diferente (revisar si usa PBIP)
- Home y Usage Dashboard NO requieren cambios (no cargan PBIP)

---

## 🤖 Migración Automática (Recomendada)

Para automatizar el proceso, usa el script de migración:

### Opción A: Preview (Dry Run)
```bash
cd ypf_bi_monitor
python scripts/migrate_to_cloud.py --dry-run
```

Esto muestra qué cambiaría **SIN modificar archivos**.

### Opción B: Migrar Todas las Apps
```bash
python scripts/migrate_to_cloud.py
```

Migra automáticamente todas las apps y crea backups.

### Opción C: Migrar App Específica
```bash
python scripts/migrate_to_cloud.py --app powerbi_analyzer
```

Migra solo Power BI Analyzer.

---

## 🧪 Testing Post-Migración

### Para cada app migrada:

1. **Ejecutar app localmente**
   ```bash
   streamlit run main.py
   ```

2. **Navegar a la app migrada**
   - Click en la app en el menú lateral

3. **Probar upload**
   - Preparar proyecto PBIP de prueba
   - Comprimir en ZIP
   - Subir usando el nuevo interfaz
   - ✅ Verificar: "✅ Proyecto cargado: XXX.pbip"

4. **Probar funcionalidad**
   - Click en botón de análisis/generación
   - ✅ Verificar: Resultados se muestran correctamente
   - ✅ Verificar: Sin errores en consola

5. **Probar persistencia**
   - Refresh página (F5)
   - Ir a tab "📁 Proyectos Guardados"
   - ✅ Verificar: Proyecto anterior aparece en lista
   - Seleccionar proyecto guardado
   - ✅ Verificar: Funciona sin re-upload

---

## 📸 Comparación Visual (Antes vs Después)

### ANTES (Local)
```
┌─────────────────────────────────────────────┐
│  📊 Power BI Analyzer                       │
├─────────────────────────────────────────────┤
│                                             │
│  📁 Ruta al archivo .pbip                   │
│  ┌─────────────────────────────────────┐   │
│  │ C:/Users/usuario/...                │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  [Analizar]                                 │
└─────────────────────────────────────────────┘

❌ Problemas:
- Usuario debe copiar/pegar ruta completa
- Propenso a errores de tipeo
- No funciona en cloud (no hay C:/)
```

### DESPUÉS (Cloud-Ready)
```
┌─────────────────────────────────────────────┐
│  📊 Power BI Analyzer                       │
├─────────────────────────────────────────────┤
│                                             │
│  📂 Cargar Proyecto PBIP                    │
│  ┌─────────────────────────────────────┐   │
│  │ 📤 Subir Nuevo  │ 📁 Proyectos      │   │
│  │    Proyecto     │    Guardados      │   │
│  ├─────────────────┼───────────────────┤   │
│  │                 │                   │   │
│  │ [Browse files]  │ • MiReporte.pbip  │   │
│  │  or drag & drop │ • Ventas_Q1.pbip  │   │
│  │                 │ • Marketing.pbip  │   │
│  └─────────────────┴───────────────────┘   │
│                                             │
│  ✅ Proyecto cargado: MiReporte.pbip        │
│                                             │
│  [🔍 Analizar Proyecto]                     │
└─────────────────────────────────────────────┘

✅ Mejoras:
- UI intuitiva con drag & drop
- Persistencia automática
- Funciona en local Y cloud
- Validación automática
```

---

## 🐛 Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'shared.pbip_loader'"

**Causa:** El archivo `shared/pbip_loader.py` no existe

**Solución:**
```bash
# Verificar que existe
ls shared/pbip_loader.py

# Si no existe, descargarlo del repo
git pull origin main
```

---

### ❌ "NameError: name 'load_pbip_cloud_ready' is not defined"

**Causa:** Olvidaste agregar el import

**Solución:** Agregar al inicio del archivo:
```python
from shared.pbip_loader import load_pbip_cloud_ready
```

---

### ❌ La app muestra error pero funciona local

**Causa:** Conflicto con código antiguo

**Solución:**
1. Verificar que eliminaste TODAS las validaciones de path antiguas
2. Buscar y eliminar:
   ```python
   if pbip_path and not Path(pbip_path).exists():
   ```

---

### ❌ Upload de ZIP no funciona

**Causa:** Límite de tamaño excedido

**Solución:** Aumentar límite en `.streamlit/config.toml`:
```toml
[server]
maxUploadSize = 500  # MB
```

---

## ✅ Validación Final

### Checklist por App

Para cada app migrada, verificar:

- [ ] Import agregado: `from shared.pbip_loader import load_pbip_cloud_ready`
- [ ] text_input reemplazado con `load_pbip_cloud_ready()`
- [ ] Key única configurada (ej: `"analyzer_upload"`)
- [ ] Validación de path eliminada
- [ ] App ejecuta sin errores
- [ ] Upload de ZIP funciona
- [ ] Análisis/generación funciona
- [ ] Proyectos guardados aparecen en lista
- [ ] Sin regresiones (features existentes funcionan)

---

## 📚 Recursos Adicionales

- **Ejemplo Completo:** [examples/powerbi_analyzer_cloud.py](examples/powerbi_analyzer_cloud.py)
- **Módulo Loader:** [shared/pbip_loader.py](shared/pbip_loader.py)
- **Script de Migración:** [scripts/migrate_to_cloud.py](scripts/migrate_to_cloud.py)
- **Plan Completo:** [CLOUDERA_MIGRATION_PLAN.md](CLOUDERA_MIGRATION_PLAN.md)

---

## 🎯 Timeline Estimado

| Actividad | Tiempo | Acumulado |
|-----------|--------|-----------|
| Leer documentación | 15 min | 15 min |
| Migrar Power BI Analyzer | 15 min | 30 min |
| Testing Analyzer | 10 min | 40 min |
| Migrar Documentation Generator | 15 min | 55 min |
| Testing DocGen | 10 min | 65 min |
| Migrar DAX Optimizer | 10 min | 75 min |
| Testing DAX | 10 min | 85 min |
| Migrar Layout Organizer | 10 min | 95 min |
| Testing Layout | 10 min | 105 min |
| Migrar BI Bot (si aplica) | 15 min | 120 min |
| Testing BI Bot | 10 min | 130 min |
| Testing integración completa | 20 min | 150 min |

**Total:** ~2.5 horas para migrar todas las apps manualmente

**Con script automático:** ~30 minutos (incluyendo testing)

---

**¿Preguntas?** Ver [CLOUDERA_SETUP.md](CLOUDERA_SETUP.md) o contactar IT Analytics - YPF S.A.

**¡Éxito con la migración!** 🚀

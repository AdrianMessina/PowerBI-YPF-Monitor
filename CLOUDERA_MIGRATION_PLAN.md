# Plan de Migración: YPF BI Monitor → Cloudera AI Workbench

**Fecha:** 2026-05-18  
**Objetivo:** Adaptar YPF BI Monitor para funcionar en Cloudera AI Workbench  
**Desafío Principal:** Gestión de archivos PBIP en ambiente cloud sin acceso a sistema de archivos local

---

## 📊 Arquitectura Actual vs Cloud

### Arquitectura Local (Actual)
```
Usuario → Ingresa ruta C:/Users/.../proyecto.pbip
         ↓
YPF BI Monitor → Lee directamente del sistema de archivos
         ↓
Procesa estructura PBIP:
  - proyecto.pbip
  - proyecto.SemanticModel/definition/*.tmdl
  - proyecto.Report/*.json
```

### Arquitectura Cloud (Propuesta)
```
Usuario → Sube archivo/carpeta PBIP
         ↓
Storage persistente de Cloudera (NFS)
         ↓
YPF BI Monitor → Lee desde workspace storage
         ↓
Procesa igual que antes
```

---

## 🎯 Opciones de Implementación

### **OPCIÓN 1: File Uploader con ZIP** ⭐ (RECOMENDADA para MVP)

**Descripción:**
- Usuario comprime su proyecto PBIP en un ZIP
- Usa `st.file_uploader()` para subir el ZIP
- La app descomprime en `/tmp` o workspace storage
- Procesa normalmente

**Ventajas:**
- ✅ Implementación rápida (2-3 horas)
- ✅ No requiere cambios en parsers existentes
- ✅ Funciona sin configuración adicional de Cloudera
- ✅ Permite demo inmediato

**Desventajas:**
- ⚠️ Usuario debe comprimir manualmente
- ⚠️ Archivos temporales (se borran al reiniciar sesión)
- ⚠️ Límite de tamaño de upload (200MB por defecto en Streamlit)

**Complejidad:** 🟢 BAJA

**Código necesario:**
```python
# En apps/powerbi_analyzer.py
uploaded_file = st.file_uploader("Sube tu proyecto PBIP (ZIP)", type=['zip'])

if uploaded_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Extraer ZIP
        zip_path = Path(tmpdir) / "proyecto.zip"
        zip_path.write_bytes(uploaded_file.read())
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)
        
        # Buscar .pbip
        pbip_files = list(Path(tmpdir).rglob("*.pbip"))
        if pbip_files:
            pbip_path = str(pbip_files[0])
            # Procesar normalmente
            results = analyze_powerbi_file(pbip_path)
```

---

### **OPCIÓN 2: Storage Persistente de Cloudera**

**Descripción:**
- Crear carpeta `pbip_projects/` en el workspace de Cloudera
- Usuario sube archivos via interfaz de Cloudera o Git
- La app lista proyectos disponibles en dropdown
- Usuario selecciona qué proyecto analizar

**Ventajas:**
- ✅ Proyectos persisten entre sesiones
- ✅ Multi-usuario puede compartir proyectos
- ✅ Integración nativa con Cloudera
- ✅ No hay límites de tamaño

**Desventajas:**
- ⚠️ Requiere setup inicial del workspace
- ⚠️ Usuario debe aprender a subir archivos a Cloudera
- ⚠️ Configuración de permisos si es multi-usuario

**Complejidad:** 🟡 MEDIA

**Estructura sugerida:**
```
/home/cdsw/
├── ypf_bi_monitor/          # Código de la app
│   ├── main.py
│   ├── apps/
│   └── ...
└── pbip_projects/            # ← NUEVA carpeta para PBIPs
    ├── Ventas_2026/
    │   ├── Ventas_2026.pbip
    │   ├── Ventas_2026.SemanticModel/
    │   └── Ventas_2026.Report/
    └── Marketing_Dashboard/
        └── ...
```

**Código necesario:**
```python
# apps/powerbi_analyzer.py
PROJECTS_DIR = Path("/home/cdsw/pbip_projects")

# Listar proyectos disponibles
pbip_files = list(PROJECTS_DIR.rglob("*.pbip"))
project_names = [f.stem for f in pbip_files]

selected_project = st.selectbox("Selecciona un proyecto", project_names)

if selected_project:
    pbip_path = next(f for f in pbip_files if f.stem == selected_project)
    results = analyze_powerbi_file(str(pbip_path))
```

---

### **OPCIÓN 3: Integración con Git**

**Descripción:**
- Proyectos PBIP se versionan en Git (Azure DevOps / GitHub)
- Cloudera clona el repositorio
- La app lee desde el repo clonado
- Permite `git pull` para actualizar proyectos

**Ventajas:**
- ✅ Versionamiento automático
- ✅ Colaboración en equipo
- ✅ Auditoría de cambios (quien modificó qué)
- ✅ Integración con CI/CD futuro

**Desventajas:**
- ⚠️ Requiere configurar autenticación Git en Cloudera
- ⚠️ Usuarios deben saber usar Git
- ⚠️ Setup más complejo

**Complejidad:** 🔴 ALTA (para fase inicial)

**Mejor como:** Fase 2, después del MVP

---

### **OPCIÓN 4: Híbrida (Upload + Persistencia)** ⭐ (RECOMENDADA para Producción)

**Descripción:**
- Combina Opción 1 y 2
- Usuario puede SUBIR nuevo proyecto (ZIP) O seleccionar uno existente
- Al subir, se guarda en storage persistente
- Crea una librería de proyectos analizados

**Ventajas:**
- ✅ Flexibilidad máxima
- ✅ UX amigable
- ✅ Proyectos se guardan automáticamente
- ✅ Mejor experiencia para usuarios recurrentes

**Desventajas:**
- ⚠️ Requiere gestión de storage (limpieza de proyectos viejos)
- ⚠️ Implementación más compleja

**Complejidad:** 🟡 MEDIA-ALTA

**Flujo de usuario:**
```
1. Usuario llega a Power BI Analyzer
2. Ve dos opciones:
   - [Tab 1] Subir nuevo proyecto (ZIP)
   - [Tab 2] Usar proyecto existente (dropdown)
3. Si sube nuevo:
   - Se descomprime en /pbip_projects/
   - Se agrega a la lista de disponibles
   - Se analiza automáticamente
4. Si selecciona existente:
   - Se carga directamente
```

---

## 🚀 Roadmap de Implementación

### **Fase 1: MVP (1-2 días)**
- ✅ Implementar Opción 1 (File Uploader con ZIP)
- ✅ Probar en Cloudera AI Workbench
- ✅ Validar que todos los módulos funcionan
- ✅ Crear documentación de uso

### **Fase 2: Persistencia (3-5 días)**
- ✅ Implementar Opción 4 (Híbrida)
- ✅ Agregar gestión de proyectos guardados
- ✅ Permitir eliminar proyectos antiguos
- ✅ Dashboard de proyectos analizados

### **Fase 3: Integración Git (1-2 semanas)**
- ✅ Conectar con Azure DevOps de YPF
- ✅ Autenticación automática
- ✅ Sincronización automática de proyectos

---

## 📋 Checklist Pre-Deployment en Cloudera

### Requisitos del Workspace
- [ ] Python 3.10+ instalado
- [ ] Permisos de escritura en `/home/cdsw/`
- [ ] Memoria: mínimo 4GB (recomendado 8GB para proyectos grandes)
- [ ] CPU: 2 cores mínimo
- [ ] Storage: 20GB mínimo (para proyectos PBIP)

### Configuración de Red
- [ ] Acceso a internet para pip install
- [ ] Si red corporativa YPF: configurar proxy (`http://proxy-azure`)
- [ ] Puertos: 8501 (Streamlit) debe estar abierto

### Variables de Entorno
```bash
# .env en Cloudera
YPF_BI_ADMIN_PASSWORD=<contraseña_admin>
PBIP_STORAGE_PATH=/home/cdsw/pbip_projects
MAX_UPLOAD_SIZE_MB=500
```

### Dependencias Adicionales
```txt
# Agregar a requirements.txt
zipfile36>=0.1.3  # Para Python 3.10+
```

---

## 🔍 Cambios en el Código (Opción 1 - MVP)

### Archivos a Modificar

1. **apps/powerbi_analyzer.py**
   - Reemplazar `st.text_input("Ruta al archivo PBIP")` 
   - Por `st.file_uploader("Sube proyecto PBIP (ZIP)")`
   - Agregar lógica de extracción de ZIP

2. **apps/documentation_generator.py**
   - Mismo cambio que analyzer

3. **apps/dax_optimizer.py**
   - Mismo cambio que analyzer

4. **apps/layout_organizer.py**
   - Mismo cambio que analyzer

5. **apps/bi_bot.py**
   - Adaptar carga de modelo

### Nuevo Módulo: `shared/pbip_loader.py`
```python
"""
Shared PBIP loader for Cloudera environment
Handles ZIP upload and extraction
"""
import streamlit as st
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Tuple

def load_pbip_from_upload() -> Optional[str]:
    """
    Shows file uploader and extracts PBIP project
    
    Returns:
        Path to .pbip file if successful, None otherwise
    """
    st.markdown("### 📂 Cargar Proyecto PBIP")
    
    uploaded_file = st.file_uploader(
        "Sube tu proyecto PBIP comprimido (ZIP)",
        type=['zip'],
        help="Comprime la carpeta completa de tu proyecto PBIP antes de subir"
    )
    
    if not uploaded_file:
        st.info("👆 Sube un archivo ZIP con tu proyecto PBIP para comenzar")
        return None
    
    try:
        # Create temp directory
        tmpdir = tempfile.mkdtemp(prefix="pbip_")
        
        # Save and extract ZIP
        zip_path = Path(tmpdir) / uploaded_file.name
        zip_path.write_bytes(uploaded_file.read())
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)
        
        # Find .pbip file
        pbip_files = list(Path(tmpdir).rglob("*.pbip"))
        
        if not pbip_files:
            st.error("❌ No se encontró archivo .pbip en el ZIP")
            return None
        
        if len(pbip_files) > 1:
            st.warning(f"⚠️ Se encontraron {len(pbip_files)} archivos .pbip. Usando el primero.")
        
        pbip_path = str(pbip_files[0])
        st.success(f"✅ Proyecto cargado: {pbip_files[0].name}")
        
        return pbip_path
        
    except zipfile.BadZipFile:
        st.error("❌ El archivo no es un ZIP válido")
        return None
    except Exception as e:
        st.error(f"❌ Error al extraer el proyecto: {str(e)}")
        return None
```

---

## 📊 Comparativa de Opciones

| Criterio | Opción 1 (ZIP Upload) | Opción 2 (Storage) | Opción 3 (Git) | Opción 4 (Híbrida) |
|----------|----------------------|-------------------|----------------|-------------------|
| **Tiempo implementación** | 2-3 horas | 1-2 días | 1-2 semanas | 3-5 días |
| **Complejidad técnica** | Baja | Media | Alta | Media-Alta |
| **Experiencia usuario** | Básica | Buena | Excelente | Excelente |
| **Persistencia** | No | Sí | Sí | Sí |
| **Colaboración** | No | Sí (manual) | Sí (automática) | Sí (manual) |
| **Versionamiento** | No | No | Sí | No |
| **Setup requerido** | Ninguno | Crear carpeta | Config Git + Auth | Crear carpeta |
| **Ideal para** | Demo/POC | Producción simple | Producción enterprise | Producción balanceada |

---

## 🎯 Recomendación Final

### Para esta semana (Demo/Validación):
**Opción 1** - File Uploader con ZIP
- Implementación rápida
- Validar que todo funciona en Cloudera
- Mostrar a stakeholders

### Para producción (próximas 2-3 semanas):
**Opción 4** - Híbrida
- Mejor UX
- Persistencia de proyectos
- Escalable

### Futuro (Q3 2026):
**Opción 3** - Integración Git
- Cuando haya múltiples equipos usando la herramienta
- Cuando se necesite auditoría completa

---

## 📝 Próximos Pasos

1. **Validar acceso a Cloudera AI Workbench**
   - [ ] Confirmar que tienes workspace creado
   - [ ] Probar subir archivos
   - [ ] Verificar Python version

2. **Implementar Opción 1 (MVP)**
   - [ ] Crear `shared/pbip_loader.py`
   - [ ] Modificar `apps/powerbi_analyzer.py`
   - [ ] Probar con proyecto PBIP real

3. **Deploy en Cloudera**
   - [ ] Clonar repo en workspace
   - [ ] Instalar dependencias
   - [ ] Ejecutar `streamlit run main.py`
   - [ ] Probar todas las apps

4. **Documentación**
   - [ ] Crear `CLOUDERA_SETUP.md` con instrucciones
   - [ ] Actualizar README.md con sección cloud
   - [ ] Crear video tutorial (opcional)

---

## 🤝 Soporte

**Dudas técnicas:** IT Analytics - YPF S.A.  
**Documentación Cloudera:** [Cloudera AI Workbench Docs](https://docs.cloudera.com/machine-learning/cloud/workspaces/)  
**MCP Server Cloudera:** [GitHub Repo](https://github.com/cloudera/CAI_Workbench_MCP_Server)

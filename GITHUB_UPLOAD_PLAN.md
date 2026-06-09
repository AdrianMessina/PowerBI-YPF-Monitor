# 📤 Plan de Subida a GitHub - YPF BI Monitor

**Repositorio:** https://github.com/AdrianMessina/Power-BI-YPF-Monitor  
**Total archivos:** 126 archivos divididos en 4 grupos  
**Seguridad:** ✅ VERIFICADA (0 issues)

---

## ⚠️ IMPORTANTE - Leer Antes de Empezar

1. **Antes del primer commit:**
   - Verifica que `.env` NO esté en el directorio (debe estar solo `.env.example`)
   - Verifica que `logs/` esté vacío o no exista
   - `.env.ypf.example` NO se debe subir (está en .gitignore)

2. **Después de cada push:**
   - Verifica en GitHub que los archivos estén correctos
   - Verifica que NO aparezca `.env` ni `logs/` en GitHub

3. **Si algo sale mal:**
   - NO hagas `git push --force` sin consultar
   - Usa `git reset --soft HEAD~1` para deshacer el último commit local

---

## 🚀 GRUPO 1 - Core Setup (34 archivos)

### Contenido
```
Archivos raíz (25):
  - main.py
  - requirements.txt
  - README.md, INSTALL.md
  - CLOUDERA_MIGRATION_PLAN.md
  - CLOUDERA_SETUP.md
  - QUICK_START_CLOUD.md
  - DEPLOYMENT_SUMMARY.md
  - MIGRATION_INSTRUCTIONS.md
  - README_CLOUD.md
  - SECURITY.md
  - PRE_GITHUB_CHECKLIST.md
  - .env.example
  - .gitignore
  - run_app.bat, run_app.sh
  - create_desktop_shortcut.ps1

Carpetas:
  - .streamlit/ (1): config.toml
  - config/ (2): configuración
  - scripts/ (3): verify_security.py, migrate_to_cloud.py, migrate_logs.py
  - examples/ (1): powerbi_analyzer_cloud.py
  - assets/ (1): logo_ypf.png
  - templates/ (1): plantilla_corporativa_ypf.docx
```

### Comandos

```bash
# 1. Inicializar Git (solo primera vez)
cd "c:\Users\SE46958\1 - Claude - Proyecto viz\ypf_bi_monitor"
git init

# 2. Conectar con GitHub
git remote add origin https://github.com/AdrianMessina/Power-BI-YPF-Monitor.git

# 3. Traer lo que ya existe en GitHub (apps_core/)
git pull origin main --allow-unrelated-histories

# 4. Agregar archivos del GRUPO 1
git add *.py *.md *.txt *.bat *.sh *.ps1 .gitignore
git add .streamlit/
git add config/
git add scripts/
git add examples/
git add assets/
git add templates/

# 5. Verificar qué se va a subir
git status

# 6. Commit
git commit -m "Grupo 1: Core setup - docs, config, scripts, templates

- Documentacion cloud (Cloudera migration, setup, deployment)
- Configuracion base (.streamlit, config/)
- Scripts de seguridad y migracion
- Templates y assets
- README, INSTALL, requirements.txt
"

# 7. Push
git push -u origin main
```

---

## 🚀 GRUPO 2 - Apps + Shared (13 archivos)

### Contenido
```
apps/ (8):
  - app_analyzer.py
  - app_docgen.py
  - app_dax.py
  - app_layout.py
  - app_bot.py
  - app_dashboard.py
  - (otros archivos apps/)

shared/ (5):
  - auth.py
  - usage_logger.py
  - pbip_loader.py
  - utils.py
  - __init__.py
```

### Comandos

```bash
cd "c:\Users\SE46958\1 - Claude - Proyecto viz\ypf_bi_monitor"

# Agregar apps/ y shared/
git add apps/
git add shared/

# Verificar
git status

# Commit
git commit -m "Grupo 2: Apps principales + Shared modules

- 6 aplicaciones Streamlit (Analyzer, DocGen, DAX, Layout, Bot, Dashboard)
- Modulos compartidos (auth, usage_logger, pbip_loader)
- Sistema de autenticacion modular
- Logger de metricas de uso
- Cloud-ready PBIP loader
"

# Push
git push
```

---

## 🚀 GRUPO 3 - Apps Core Sin DocGen (27 archivos)

### Contenido
```
apps_core/analyzer_core/ (7)
apps_core/dax_core/ (7)
apps_core/layout_core/ (4)
apps_core/bot_core/ (9)
```

### Comandos

```bash
cd "c:\Users\SE46958\1 - Claude - Proyecto viz\ypf_bi_monitor"

# Agregar apps_core/ SIN docgen_core/
git add apps_core/analyzer_core/
git add apps_core/dax_core/
git add apps_core/layout_core/
git add apps_core/bot_core/
git add apps_core/__init__.py

# Verificar
git status

# Commit
git commit -m "Grupo 3: Apps Core - Analyzer, DAX, Layout, Bot

- Analyzer Core: Analisis de Power BI files
- DAX Core: Optimizacion de medidas DAX
- Layout Core: Organizador de layout de reportes
- Bot Core: AI assistant para Power BI
"

# Push
git push
```

---

## 🚀 GRUPO 4 - DocGen (51 archivos)

### Contenido
```
apps_core/docgen_core/ (51 archivos):
  - core/
  - document_generation/
  - visualization/
  - utils/
  - (todos los submodulos)
```

### Comandos

```bash
cd "c:\Users\SE46958\1 - Claude - Proyecto viz\ypf_bi_monitor"

# Agregar docgen_core/
git add apps_core/docgen_core/

# Verificar
git status

# Commit
git commit -m "Grupo 4: DocGen Core - Generador de documentacion

- Sistema completo de generacion de documentacion Power BI
- Parsers PBIP/TMDL
- Validators de semantic models
- Analyzers de relaciones, medidas, columnas
- Section generators para Word
- Visualizacion de diagramas
- 51 archivos - el modulo mas completo del proyecto
"

# Push
git push
```

---

## ✅ Verificación Final

Después de subir los 4 grupos, verificar en GitHub que existan:

### Archivos Críticos
- ✅ main.py
- ✅ requirements.txt
- ✅ README.md
- ✅ .gitignore
- ✅ .env.example (con valores genéricos)

### Carpetas Críticas
- ✅ apps/
- ✅ apps_core/ (con todos los core modules)
- ✅ shared/
- ✅ config/
- ✅ scripts/
- ✅ templates/
- ✅ .streamlit/

### Archivos que NO Deben Estar
- ❌ .env (valores reales)
- ❌ .env.ypf.example (config interna YPF)
- ❌ logs/ (logs de uso)
- ❌ venv/ (entorno virtual)
- ❌ __pycache__/

---

## 🔄 Después de Subir Todo

### En Cloudera Terminal

```bash
# 1. Ir al directorio del proyecto
cd /home/cdsw

# 2. Traer todos los archivos nuevos
git pull origin main

# 3. Verificar que todo esté
ls -la
ls apps/
ls shared/
ls apps_core/

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Crear .env con config YPF
nano .env
# Pegar config de .env.ypf.example

# 6. Crear directorio para PBIP storage
mkdir -p /home/cdsw/pbip_projects

# 7. Correr la app
streamlit run main.py
```

---

## 📊 Resumen de Archivos por Grupo

| Grupo | Archivos | Descripción |
|-------|----------|-------------|
| 1 - Core Setup | 34 | Docs, config, scripts, templates |
| 2 - Apps + Shared | 13 | Aplicaciones y módulos compartidos |
| 3 - Apps Core (sin DocGen) | 27 | Analyzer, DAX, Layout, Bot cores |
| 4 - DocGen | 51 | Generador de documentación completo |
| **TOTAL** | **125** | **Proyecto completo** |

---

## 🚨 Si Algo Sale Mal

### Deshacer último commit (antes de push)
```bash
git reset --soft HEAD~1
```

### Deshacer último push (PELIGROSO)
```bash
# Solo si es absolutamente necesario
git push --force-with-lease origin main
```

### Ver qué se va a subir
```bash
git status
git diff --cached
```

### Verificar commits
```bash
git log --oneline
```

---

**Creado:** 2026-05-18  
**Proyecto:** YPF BI Monitor Suite v1.0  
**Seguridad:** ✅ Verificada con scripts/verify_security.py

# Guía de Despliegue: YPF BI Monitor en Cloudera AI Workbench

**Fecha:** 2026-05-18  
**Versión:** 1.0  
**Tiempo estimado:** 30-45 minutos

---

## 📋 Requisitos Previos

### Acceso a Cloudera AI Workbench
- [ ] Cuenta activa en Cloudera AI Workbench
- [ ] Workspace/Proyecto creado
- [ ] Permisos de ejecución de código

### Especificaciones Mínimas del Workspace
- **Python:** 3.10 o superior
- **Memoria:** 4 GB (recomendado 8 GB para proyectos grandes)
- **CPU:** 2 cores mínimo
- **Storage:** 20 GB (para almacenar proyectos PBIP)
- **Runtime:** Python o Workbench (no JupyterLab, necesitamos terminal)

---

## 🚀 Paso 1: Crear y Configurar Workspace

### 1.1 Crear Nuevo Proyecto en Cloudera

1. Login en Cloudera AI Workbench
2. Click en **"Create a new project"**
3. Configuración:
   - **Project Name:** `YPF BI Monitor`
   - **Description:** `Suite de herramientas para análisis de Power BI`
   - **Visibility:** `Private` (o según política de YPF)
   - **Initial Setup:** Git repository

### 1.2 Configurar Git Repository

**Opción A: Desde GitHub/Azure DevOps**
```
Git URL: <URL_de_tu_repositorio_YPF_BI_Monitor>
Branch: main
```

**Opción B: Upload manual**
- Skip Git setup
- Subiremos archivos manualmente en Paso 2

---

## 🚀 Paso 2: Subir Código al Workspace

### Opción A: Via Git (Recomendado)

El código ya está en el workspace si configuraste Git en Paso 1.1

### Opción B: Upload Manual

1. Comprimir todo el proyecto localmente:
   ```bash
   # En tu máquina local
   cd c:\Users\SE46958\1 - Claude - Proyecto viz\ypf_bi_monitor
   # Crear ZIP excluyendo venv y cache
   zip -r ypf_bi_monitor.zip . -x "venv/*" "**/__pycache__/*" "*.pyc"
   ```

2. En Cloudera AI Workbench:
   - Click en **"Files"** en el panel izquierdo
   - Click en **"Upload"** → **"Upload Files"**
   - Seleccionar `ypf_bi_monitor.zip`
   - Extraer: Click derecho → **"Extract"**

---

## 🚀 Paso 3: Abrir Terminal en Cloudera

1. En tu proyecto, click en **"Workbench"** (panel izquierdo)
2. Click en **"New Session"** o **"Open Terminal"**
3. Configurar sesión:
   - **Editor:** Terminal o JupyterLab (con terminal)
   - **Kernel:** Python 3.10+
   - **Resource Profile:** 4 GB / 2 CPU (mínimo)

4. Click **"Launch"**

Deberías ver una terminal similar a:
```
[cdsw@<session-id> ~]$
```

---

## 🚀 Paso 4: Verificar Python y Crear Entorno Virtual

### 4.1 Verificar Python

```bash
python --version
# Debe mostrar: Python 3.10.x o superior
```

Si no está disponible, intentar:
```bash
python3 --version
```

### 4.2 Navegar al Proyecto

```bash
cd /home/cdsw/ypf_bi_monitor
ls -la
```

Deberías ver:
```
main.py
apps/
apps_core/
shared/
requirements.txt
...
```

### 4.3 Crear Entorno Virtual

```bash
python -m venv venv
```

### 4.4 Activar Entorno Virtual

```bash
source venv/bin/activate
```

Verás `(venv)` al inicio de tu prompt:
```
(venv) [cdsw@<session-id> ypf_bi_monitor]$
```

---

## 🚀 Paso 5: Configurar Proxy (Si Red Corporativa YPF)

### Verificar si necesitas proxy

¿Estás en red corporativa YPF? → Necesitas configurar proxy

### Configurar Variables de Entorno

```bash
export HTTPS_PROXY=http://proxy-azure
export HTTP_PROXY=http://proxy-azure
export NO_PROXY=localhost,127.0.0.1,*.cloudera.site
```

### Hacerlo Permanente (Opcional)

```bash
cat >> ~/.bashrc << 'EOF'
# YPF Corporate Proxy
export HTTPS_PROXY=http://proxy-azure
export HTTP_PROXY=http://proxy-azure
export NO_PROXY=localhost,127.0.0.1,*.cloudera.site
EOF

source ~/.bashrc
```

---

## 🚀 Paso 6: Instalar Dependencias

### 6.1 Actualizar pip

```bash
pip install --upgrade pip
```

### 6.2 Instalar Requirements

```bash
pip install -r requirements.txt
```

**Tiempo estimado:** 3-5 minutos

**Posibles problemas:**

**❌ Error: "Connection timeout to pypi.org"**
```bash
# Verificar proxy
echo $HTTPS_PROXY
# Si está vacío, volver a Paso 5
```

**❌ Error con weasyprint (opcional)**
```bash
# weasyprint es opcional (solo para exportar PDF)
# La app funciona sin él
# Si falla, instalar sin weasyprint:
pip install -r requirements.txt --ignore-requires-python
```

### 6.3 Verificar Instalación

```bash
pip list | grep streamlit
# Debe mostrar: streamlit  1.31.0 o superior
```

---

## 🚀 Paso 7: Configurar Variables de Entorno

### 7.1 Crear archivo .env

```bash
cp .env.example .env
nano .env
```

### 7.2 Configurar Variables

```env
# ============================================================
# YPF BI Monitor - Cloud Configuration
# ============================================================

# Admin password for Usage Dashboard
YPF_BI_ADMIN_PASSWORD=YPF_admin_2026

# PBIP Storage Path (persistent storage for uploaded projects)
PBIP_STORAGE_PATH=/home/cdsw/pbip_projects

# Max upload size in MB
MAX_UPLOAD_SIZE_MB=500

# Logging backend (file or postgres)
LOG_BACKEND=file

# File logging path
LOG_FILE_PATH=/home/cdsw/ypf_bi_monitor/logs/usage.log
```

Guardar y cerrar (Ctrl+X, luego Y, luego Enter)

### 7.3 Crear Carpeta de Almacenamiento

```bash
mkdir -p /home/cdsw/pbip_projects
mkdir -p /home/cdsw/ypf_bi_monitor/logs
```

---

## 🚀 Paso 8: Ejecutar la Aplicación

### 8.1 Primera Ejecución

```bash
streamlit run main.py
```

Verás una salida similar a:
```
  You can now view your Streamlit app in your browser.

  Network URL: http://<session-url>:8501
  External URL: http://<external-ip>:8501
```

### 8.2 Acceder a la Aplicación

**En Cloudera AI Workbench:**

1. Cloudera automáticamente detecta el puerto 8501
2. Verás un botón **"Open"** o similar junto a la sesión
3. Click en **"Open"** → Se abre en nueva pestaña

**URL directa:**
```
https://<tu-workspace>.cloudera.site/<session-id>/8501
```

### 8.3 Verificar que Funciona

✅ Deberías ver:
- Logo de YPF
- Menú lateral con las apps
- Página de inicio "YPF BI Monitor"

---

## 🚀 Paso 9: Probar la Funcionalidad Cloud

### 9.1 Preparar Proyecto PBIP de Prueba

En tu **máquina local**:

1. Abre Power BI Desktop
2. Abre un reporte de prueba
3. **Archivo → Guardar como → Power BI Project (.pbip)**
4. Guarda en: `C:\Temp\TestReport`
5. **Comprimir** la carpeta completa:
   - Click derecho en `TestReport` → **"Comprimir en ZIP"**
   - Resultado: `TestReport.zip`

### 9.2 Probar Upload en Cloudera

1. En YPF BI Monitor (en Cloudera), ir a **"Power BI Analyzer"**
2. Verás la nueva interfaz: **"📂 Cargar Proyecto PBIP"**
3. Click en **"Browse files"** o arrastrar `TestReport.zip`
4. Esperar upload y extracción
5. ✅ Deberías ver: **"✅ Proyecto cargado: TestReport.pbip"**
6. Click en **"🔍 Analizar Proyecto"**
7. ✅ Deberías ver los resultados del análisis

### 9.3 Verificar Persistencia

1. Refresh la página (F5)
2. Ir a **"Power BI Analyzer"** nuevamente
3. Click en tab **"📁 Proyectos Guardados"**
4. ✅ Deberías ver **"TestReport"** en la lista
5. Seleccionarlo y usar sin volver a subir

---

## 🚀 Paso 10: Configurar Ejecución Automática (Opcional)

Para que la app se ejecute automáticamente al iniciar el workspace:

### 10.1 Crear Script de Inicio

```bash
cat > /home/cdsw/start_ypf_bi_monitor.sh << 'EOF'
#!/bin/bash
cd /home/cdsw/ypf_bi_monitor
source venv/bin/activate
streamlit run main.py --server.port=8501 --server.headless=true
EOF

chmod +x /home/cdsw/start_ypf_bi_monitor.sh
```

### 10.2 Configurar en Cloudera

1. En el proyecto, ir a **"Settings"** → **"Environment"**
2. En **"Startup Script"**, agregar:
   ```bash
   /home/cdsw/start_ypf_bi_monitor.sh
   ```
3. Guardar

Ahora, cada vez que inicies una sesión, la app arrancará automáticamente.

---

## 🎯 Resumen de URLs Importantes

Una vez desplegado:

| Recurso | URL |
|---------|-----|
| **App Principal** | `https://<workspace>.cloudera.site/<session>/8501` |
| **Logs** | `/home/cdsw/ypf_bi_monitor/logs/usage.log` |
| **Proyectos PBIP** | `/home/cdsw/pbip_projects/` |
| **Código** | `/home/cdsw/ypf_bi_monitor/` |

---

## ❓ Troubleshooting

### ❌ Error: "Address already in use: 8501"

**Causa:** Ya hay otra instancia de Streamlit corriendo

**Solución:**
```bash
pkill -f streamlit
streamlit run main.py
```

---

### ❌ Error: "ModuleNotFoundError: No module named 'streamlit'"

**Causa:** Entorno virtual no activado

**Solución:**
```bash
source /home/cdsw/ypf_bi_monitor/venv/bin/activate
pip install -r requirements.txt
```

---

### ❌ Error: "Permission denied" al crear carpetas

**Causa:** No tienes permisos de escritura

**Solución:**
```bash
# Verificar permisos
ls -la /home/cdsw

# Si es tu workspace, deberías tener permisos
# Si no, contactar admin de Cloudera
```

---

### ❌ Upload de ZIP falla (archivo muy grande)

**Causa:** Límite de upload de Streamlit (200 MB por defecto)

**Solución:** Aumentar límite en `.streamlit/config.toml`:
```bash
mkdir -p .streamlit
cat >> .streamlit/config.toml << 'EOF'
[server]
maxUploadSize = 500
EOF
```

Reiniciar app:
```bash
pkill -f streamlit
streamlit run main.py
```

---

### ❌ No puedo acceder a la URL de la app

**Causa:** Firewall o configuración de red

**Solución:**
1. Verificar que el puerto 8501 está en uso:
   ```bash
   netstat -tulpn | grep 8501
   ```
2. Usar el botón **"Open"** de Cloudera en lugar de URL directa
3. Verificar con admin de Cloudera si hay restricciones de red

---

### ❌ Proxy no funciona / pip timeout

**Causa:** Configuración de proxy incorrecta

**Solución:**
```bash
# Verificar proxy actual
env | grep -i proxy

# Probar conectividad
curl -I https://pypi.org
# Si falla, el proxy está mal configurado

# Re-configurar (preguntar a IT por proxy correcto)
export HTTPS_PROXY=http://proxy-azure:8080  # Agregar puerto si es necesario
export HTTP_PROXY=http://proxy-azure:8080
```

---

## 📊 Métricas de Éxito

### Checkpoint 1: Instalación ✅
- [ ] Python 3.10+ disponible
- [ ] Venv creado y activado
- [ ] Todas las dependencias instaladas sin errores

### Checkpoint 2: Primera Ejecución ✅
- [ ] `streamlit run main.py` ejecuta sin errores
- [ ] Puedo acceder a la URL de la app
- [ ] Veo el logo de YPF y el menú

### Checkpoint 3: Funcionalidad Cloud ✅
- [ ] Puedo subir un ZIP con proyecto PBIP
- [ ] El proyecto se extrae correctamente
- [ ] Power BI Analyzer funciona con el proyecto subido
- [ ] El proyecto aparece en "Proyectos Guardados"

### Checkpoint 4: Producción ✅
- [ ] Múltiples proyectos PBIP funcionan
- [ ] Todas las apps funcionan (Analyzer, DocGen, DAX Optimizer, etc.)
- [ ] Logs se guardan correctamente
- [ ] Performance es aceptable (<5s para cargar app)

---

## 🔐 Seguridad y Mejores Prácticas

### Control de Acceso

```bash
# Verificar permisos de archivos sensibles
chmod 600 .env
chmod 700 /home/cdsw/pbip_projects

# Solo el owner puede leer/escribir
```

### Limpieza de Proyectos Antiguos

```bash
# Crear script de limpieza (ejecutar mensualmente)
cat > /home/cdsw/cleanup_old_projects.sh << 'EOF'
#!/bin/bash
# Eliminar proyectos PBIP no accedidos en 60 días
find /home/cdsw/pbip_projects -type d -atime +60 -exec rm -rf {} \;
echo "Cleanup completed: $(date)" >> /home/cdsw/cleanup.log
EOF

chmod +x /home/cdsw/cleanup_old_projects.sh
```

### Backup de Configuración

```bash
# Backup de .env y configuraciones
cp .env .env.backup
cp -r .streamlit .streamlit.backup
```

---

## 📚 Recursos Adicionales

- **Documentación Cloudera AI Workbench:** https://docs.cloudera.com/machine-learning/cloud/
- **Streamlit en Producción:** https://docs.streamlit.io/deploy
- **README Principal:** [README.md](README.md)
- **Plan de Migración:** [CLOUDERA_MIGRATION_PLAN.md](CLOUDERA_MIGRATION_PLAN.md)

---

## 🎉 ¡Listo!

Si completaste todos los checkpoints, tu instalación de YPF BI Monitor en Cloudera AI Workbench está lista para usar.

### Próximos Pasos

1. **Capacitar usuarios:** Mostrar cómo comprimir proyectos PBIP y subirlos
2. **Monitorear uso:** Revisar logs en `/home/cdsw/ypf_bi_monitor/logs/`
3. **Optimizar:** Ajustar recursos del workspace según demanda
4. **Iterar:** Feedback de usuarios → mejoras → deploy

---

**Desarrollado con ❤️ por IT Analytics - YPF S.A.**  
**Versión Cloud:** 1.0 | **Fecha:** 2026-05-18

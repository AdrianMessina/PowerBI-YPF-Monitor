# 🚀 Quick Start: YPF BI Monitor en Cloudera (5 minutos)

**Para:** Usuarios que quieren probar YPF BI Monitor en Cloudera AI Workbench AHORA  
**Tiempo:** 5-10 minutos  
**Prerequisito:** Acceso a Cloudera AI Workbench

---

## Paso 1️⃣: Crear Proyecto en Cloudera (2 min)

1. Login en Cloudera AI Workbench → **https://ml-1b92dce9-f6e.apdazrus.yr7q-bef3.a2.cloudera.site/home**
2. Click **"Create a new project"**
3. Configurar:
   - **Name:** `YPF BI Monitor`
   - **Git URL:** `<tu_repo>` o **skip** (upload manual después)
   - **Python Version:** 3.10+
4. Click **"Create Project"**

---

## Paso 2️⃣: Abrir Terminal (1 min)

1. En el proyecto → Click **"Workbench"** (panel izquierdo)
2. Click **"New Session"**:
   - **Editor:** Terminal
   - **Kernel:** Python 3.10
   - **Resources:** 4 GB RAM / 2 CPU
3. Click **"Launch"**

---

## Paso 3️⃣: Subir Código (1 min)

**Opción A - Si configuraste Git:**
```bash
cd /home/cdsw
git clone <tu_repo_url> ypf_bi_monitor
cd ypf_bi_monitor
```

**Opción B - Upload manual:**
1. Comprimir proyecto local (excluir `venv/`)
2. En Cloudera → **Files** → **Upload** → Subir ZIP
3. Extraer ZIP

---

## Paso 4️⃣: Instalar Dependencias (3 min)

```bash
cd /home/cdsw/ypf_bi_monitor

# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Si estás en red YPF (configurar proxy)
export HTTPS_PROXY=http://proxy-azure
export HTTP_PROXY=http://proxy-azure

# Instalar
pip install -r requirements.txt
```

---

## Paso 5️⃣: Configurar Variables (1 min)

```bash
# Crear .env
cp .env.example .env

# Crear carpeta de almacenamiento
mkdir -p /home/cdsw/pbip_projects
```

---

## Paso 6️⃣: Ejecutar App (30 seg)

```bash
streamlit run main.py
```

Verás:
```
  Network URL: http://....:8501
```

Click en **"Open"** en Cloudera o usa la URL directa.

---

## Paso 7️⃣: Probar Upload de PBIP (2 min)

### En tu PC local:
1. Abre Power BI Desktop
2. Guarda reporte como `.pbip`
3. Comprime la carpeta completa → `MiReporte.zip`

### En YPF BI Monitor (Cloudera):
1. Ir a **"Power BI Analyzer"**
2. Subir `MiReporte.zip`
3. Click **"Analizar"**

✅ **¡Listo!** Tu app está corriendo en la nube.

---

## 🆘 Problemas Comunes

**❌ "Connection timeout" al instalar:**
```bash
# Configurar proxy (si red corporativa YPF)
export HTTPS_PROXY=http://proxy-azure
export HTTP_PROXY=http://proxy-azure
pip install -r requirements.txt
```

**❌ "Port 8501 already in use":**
```bash
pkill -f streamlit
streamlit run main.py
```

**❌ "ModuleNotFoundError":**
```bash
source venv/bin/activate  # Activar entorno virtual
pip install -r requirements.txt
```

---

## 📚 Más Información

- **Guía Completa:** [CLOUDERA_SETUP.md](CLOUDERA_SETUP.md)
- **Plan de Migración:** [CLOUDERA_MIGRATION_PLAN.md](CLOUDERA_MIGRATION_PLAN.md)
- **Código Ejemplo:** [examples/powerbi_analyzer_cloud.py](examples/powerbi_analyzer_cloud.py)

---

**¿Funcionó?** ✅ Ahora puedes usar todas las apps de YPF BI Monitor desde cualquier lugar.

**¿Problemas?** 🆘 Ver [CLOUDERA_SETUP.md](CLOUDERA_SETUP.md) sección Troubleshooting.

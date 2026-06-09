# Guía de Migración a Cloud - YPF BI Monitor

**Documento para cuando te aprueben el deployment en cloud**

Esta guía te explica exactamente qué hacer para migrar la app a la nube y hacer que el dashboard de uso funcione correctamente con múltiples usuarios.

---

## 📋 Índice

1. [Antes de Empezar](#antes-de-empezar)
2. [Decisión: Qué Backend Usar](#decisión-qué-backend-usar)
3. [Opción A: Cloud Simple (SQLite)](#opción-a-cloud-simple-sqlite)
4. [Opción B: Cloud Producción (PostgreSQL)](#opción-b-cloud-producción-postgresql)
5. [Configurar Autenticación](#configurar-autenticación)
6. [Migrar Logs Existentes](#migrar-logs-existentes)
7. [Verificar que Funciona](#verificar-que-funciona)
8. [Troubleshooting](#troubleshooting)

---

## Antes de Empezar

### ¿Qué cambia al migrar a cloud?

**Situación actual (local):**
```
Usuario → App local → Logs en archivos (logs/*.jsonl) → Dashboard lee archivos
```

**Problema en cloud:**
- Cada usuario tendría sus propios archivos efímeros
- No se pueden ver los logs de otros usuarios
- Los archivos se pierden al reiniciar

**Solución cloud:**
```
Usuario 1 →                    ┌─────────────────┐
Usuario 2 → App en cloud   →   │ Base de Datos   │ → Dashboard lee BD
Usuario 3 →                    │  (SQLite o      │    (ve TODOS los logs)
                               │   PostgreSQL)   │
                               └─────────────────┘
```

### ¿Qué necesitas decidir?

1. **¿Dónde vas a deployar?**
   - Streamlit Cloud (gratis, simple)
   - Servidor Cloudera/YPF
   - Otro (AWS, Azure, etc.)

2. **¿Qué base de datos vas a usar?**
   - SQLite (simple, bueno para pocos usuarios)
   - PostgreSQL (robusto, recomendado para producción)

---

## Decisión: Qué Backend Usar

### Tabla Comparativa

| Característica | File (actual) | SQLite | PostgreSQL |
|----------------|---------------|--------|------------|
| **Setup** | ✅ Cero config | ✅ Simple | ⚠️ Requiere servidor |
| **Cloud** | ❌ No funciona bien | ✅ Funciona | ✅ Ideal |
| **Multi-usuario** | ⚠️ Solo local | ✅ Sí | ✅ Sí |
| **Escalabilidad** | ❌ Limitada | ⚠️ Media | ✅ Alta |
| **Persistencia** | ✅ Local | ✅ Archivo único | ✅ Servidor |
| **Recomendado para** | Desarrollo | Cloud simple | Producción |

### Recomendación

- **Para presentación/demo:** Mantener `file` (actual)
- **Para Streamlit Cloud:** Usar `sqlite`
- **Para Cloudera/producción:** Usar `postgres`

---

## Opción A: Cloud Simple (SQLite)

**Ideal para:** Streamlit Cloud, pocos usuarios (<50), setup rápido

### Paso 1: Instalar Dependencias

SQLite viene incluido con Python, no necesitas instalar nada adicional.

### Paso 2: Crear/Actualizar `.env`

```bash
# Copiar el ejemplo si no existe
cp .env.example .env
```

Editar `.env`:

```bash
# ============================================================
# CONFIGURACIÓN CLOUD SIMPLE (SQLite)
# ============================================================

# Autenticación
AUTH_BACKEND=local

AUTH_ADMIN_USERS=se43617,se46958,se42998,se41714,se48659,se48762,ry40860,nicolas.ursino
AUTH_DEV_MODE=false

# Logging con SQLite
LOG_BACKEND=sqlite
LOG_SQLITE_PATH=data/usage.db
LOG_ENABLED=true

# Deployment
DEPLOYMENT_ENV=cloud
APP_BASE_URL=https://tu-app.streamlit.app
```

### Paso 3: Crear Directorio para la Base de Datos

```bash
mkdir -p data
```

⚠️ **Importante para Streamlit Cloud:**

Streamlit Cloud tiene sistema de archivos efímero. La BD se perderá al reiniciar SALVO que uses un volumen persistente o servicio externo.

**Alternativa:** Usar servicio PostgreSQL gratuito como:
- [Supabase](https://supabase.com) - PostgreSQL gratis
- [Neon](https://neon.tech) - PostgreSQL serverless gratis
- [ElephantSQL](https://www.elephantsql.com) - PostgreSQL gratis (20MB)

### Paso 4: Configurar Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Conecta tu repositorio GitHub
3. En **Settings → Secrets**, agrega:

```toml
AUTH_BACKEND = "local"
AUTH_WHITELIST = ""
AUTH_ADMIN_USERS = "se43617,se46958,se42998,se41714,se48659,se48762,ry40860,nicolas.ursino"
LOG_BACKEND = "sqlite"
LOG_SQLITE_PATH = "/tmp/usage.db"
LOG_ENABLED = "true"
DEPLOYMENT_ENV = "cloud"
```

⚠️ **Nota:** `/tmp/usage.db` se perderá al reiniciar. Ver Opción B para persistencia.

### Paso 5: Deploy

Streamlit Cloud detectará `main.py` y hará deploy automáticamente.

**Listo!** ✅ El dashboard ahora mostrará logs de todos los usuarios.

---

## Opción B: Cloud Producción (PostgreSQL)

**Ideal para:** Cloudera, servidor corporativo, muchos usuarios, producción

### Paso 1: Instalar Dependencias

```bash
pip install psycopg2-binary
```

O usa el archivo de requerimientos cloud:

```bash
pip install -r requirements-cloud.txt
```

### Paso 2: Configurar PostgreSQL

#### Opción 2.1: PostgreSQL Local (Testing)

```bash
# Instalar PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Iniciar servicio
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Crear base de datos
sudo -u postgres psql

-- En el prompt de PostgreSQL:
CREATE DATABASE ypf_bi_monitor;
CREATE USER app_user WITH PASSWORD 'tu_password_seguro';
GRANT ALL PRIVILEGES ON DATABASE ypf_bi_monitor TO app_user;
\q
```

#### Opción 2.2: PostgreSQL Cloud Gratuito

**Supabase (Recomendado - Gratis):**

1. Ir a [supabase.com](https://supabase.com)
2. Crear cuenta y nuevo proyecto
3. Anotar credenciales:
   - Host: `db.xxxxx.supabase.co`
   - Port: `5432`
   - Database: `postgres`
   - User: `postgres`
   - Password: `tu-password`

**Neon (Alternativa):**

1. Ir a [neon.tech](https://neon.tech)
2. Crear proyecto
3. Copiar connection string

#### Opción 2.3: PostgreSQL Corporativo (YPF/Cloudera)

Contactar al equipo de infraestructura para obtener:
- Host del servidor PostgreSQL
- Puerto (usualmente 5432)
- Nombre de la base de datos
- Usuario y contraseña

### Paso 3: Crear/Actualizar `.env`

```bash
# ============================================================
# CONFIGURACIÓN CLOUD PRODUCCIÓN (PostgreSQL)
# ============================================================

# Autenticación
AUTH_BACKEND=local  # Cambiar a 'ldap' o 'cloudera' según corresponda

AUTH_ADMIN_USERS=se43617,se46958,se42998,se41714,se48659,se48762,ry40860,nicolas.ursino
AUTH_DEV_MODE=false

# Logging con PostgreSQL
LOG_BACKEND=postgres
LOG_POSTGRES_HOST=db.xxxxx.supabase.co  # Tu host PostgreSQL
LOG_POSTGRES_PORT=5432
LOG_POSTGRES_DB=postgres  # o ypf_bi_monitor
LOG_POSTGRES_USER=postgres  # Tu usuario
LOG_POSTGRES_PASSWORD=tu_password_aqui  # Tu password
LOG_POSTGRES_TABLE=usage_events
LOG_ENABLED=true

# Deployment
DEPLOYMENT_ENV=cloud
APP_BASE_URL=https://bi-monitor.ypf.com
```

### Paso 4: Inicializar Base de Datos

La app crea las tablas automáticamente al iniciar, pero podés hacerlo manualmente:

```bash
# Conectarse a PostgreSQL
psql -h db.xxxxx.supabase.co -U postgres -d postgres

# O si es local:
psql -U app_user -d ypf_bi_monitor
```

```sql
-- Crear tabla (opcional, la app lo hace automático)
CREATE TABLE IF NOT EXISTS usage_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    hostname VARCHAR(255) NOT NULL,
    suite VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    event VARCHAR(255) NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para mejor performance
CREATE INDEX IF NOT EXISTS idx_usage_events_timestamp ON usage_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_usage_events_username ON usage_events(username);
CREATE INDEX IF NOT EXISTS idx_usage_events_event ON usage_events(event);
CREATE INDEX IF NOT EXISTS idx_usage_events_session_id ON usage_events(session_id);

-- Verificar que funcionó
\dt
SELECT COUNT(*) FROM usage_events;
```

### Paso 5: Probar Localmente

```bash
# Asegurarse que .env está configurado
cat .env | grep LOG_BACKEND

# Ejecutar app
streamlit run main.py
```

Usa la app un poco, luego verifica que los logs se guardaron:

```bash
psql -h tu-host -U tu-user -d tu-db

SELECT COUNT(*) FROM usage_events;
SELECT * FROM usage_events ORDER BY timestamp DESC LIMIT 5;
```

### Paso 6: Deploy en Servidor

#### Si es Streamlit Cloud:

En **Settings → Secrets**:

```toml
AUTH_BACKEND = "local"
AUTH_WHITELIST = ""
AUTH_ADMIN_USERS = "se43617,se46958,se42998,se41714,se48659,se48762,ry40860,nicolas.ursino"
LOG_BACKEND = "postgres"
LOG_POSTGRES_HOST = "db.xxxxx.supabase.co"
LOG_POSTGRES_PORT = "5432"
LOG_POSTGRES_DB = "postgres"
LOG_POSTGRES_USER = "postgres"
LOG_POSTGRES_PASSWORD = "tu_password"
LOG_POSTGRES_TABLE = "usage_events"
LOG_ENABLED = "true"
```

#### Si es servidor Cloudera/Linux:

```bash
# Clonar repo
cd /opt/apps
git clone https://github.com/your-org/ypf-bi-monitor.git
cd ypf-bi-monitor

# Crear virtualenv
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements-cloud.txt

# Configurar .env
cp .env.example .env
nano .env  # Editar con credenciales de PostgreSQL

# Ejecutar
streamlit run main.py --server.port 8501 --server.address 0.0.0.0
```

**Listo!** ✅ PostgreSQL configurado y persistente.

---

## Configurar Autenticación

### Mantener Autenticación Local (Más Simple)

Si van a usar la app solo usuarios autorizados en la red YPF:

```bash
AUTH_BACKEND=local

AUTH_ADMIN_USERS=se43617,se46958,se42998,se41714,se48659,se48762,ry40860,nicolas.ursino
```

Esto funciona porque la app detecta automáticamente el usuario Windows/sistema.

### Migrar a LDAP/Cloudera (Corporativo)

Si YPF quiere autenticación corporativa:

```bash
# Para LDAP/Active Directory
AUTH_BACKEND=ldap
LDAP_SERVER=ldap.ypf.com
LDAP_PORT=389
LDAP_BASE_DN=dc=grupo,dc=ypf,dc=com
LDAP_USER_DN_TEMPLATE=cn={username},{base_dn}

# Para Cloudera
AUTH_BACKEND=cloudera
CLOUDERA_AUTH_ENDPOINT=https://cloudera.ypf.com/api/v1/auth
```

**Importante:** Para LDAP, instalar dependencia:

```bash
pip install ldap3
```

---

## Migrar Logs Existentes

Si ya tenés logs en archivos locales (`logs/usage_*.jsonl`) y querés migrarlos a PostgreSQL:

### Paso 1: Configurar PostgreSQL en `.env`

Asegurarte que `.env` tenga las credenciales correctas.

### Paso 2: Ejecutar Script de Migración

```bash
python scripts/migrate_logs_to_postgres.py
```

El script:
1. Lee todos los archivos `logs/usage_*.jsonl`
2. Los inserta en PostgreSQL
3. Muestra progreso y resumen

**Ejemplo de salida:**

```
============================================================
🚀 MIGRACIÓN DE LOGS A POSTGRESQL
============================================================

🔧 Configurando conexión a PostgreSQL...
   Host: db.xxxxx.supabase.co
   Database: postgres
   Table: usage_events
✅ Conexión exitosa a PostgreSQL

📁 Encontrados 3 archivos de logs

📄 Procesando: usage_20260405.jsonl
   ✅ 127 eventos migrados

📄 Procesando: usage_20260406.jsonl
   ✅ 89 eventos migrados

📄 Procesando: usage_20260407.jsonl
   ✅ 45 eventos migrados

============================================================
📊 RESUMEN DE MIGRACIÓN
============================================================
Total eventos encontrados:  261
Eventos migrados:           261
Errores:                    0
============================================================

✅ Migración completada exitosamente
```

### Paso 3: Verificar en PostgreSQL

```bash
psql -h tu-host -U tu-user -d tu-db

SELECT COUNT(*) FROM usage_events;
SELECT username, COUNT(*) as eventos 
FROM usage_events 
GROUP BY username 
ORDER BY eventos DESC;
```

---

## Verificar que Funciona

### ✅ Checklist de Verificación

**1. Logging funciona:**
```bash
# Ejecutar app
streamlit run main.py

# En otra terminal, verificar logs
# Si es PostgreSQL:
psql -h host -U user -d db -c "SELECT COUNT(*) FROM usage_events;"

# Si es SQLite:
sqlite3 data/usage.db "SELECT COUNT(*) FROM usage_events;"
```

**2. Dashboard muestra datos:**
- Ir a la app → Usage Dashboard
- Verificar que muestra eventos
- Verificar que muestra todos los usuarios (no solo el tuyo)

**3. Multi-usuario funciona:**
- Pedirle a otro usuario que use la app
- Verificar que sus eventos aparecen en el dashboard
- Filtrar por usuario en el dropdown del dashboard

**4. Persistencia funciona:**
- Reiniciar la app
- Verificar que los logs siguen ahí
- Dashboard debe mostrar historial completo

### 📊 Queries Útiles para Verificar

```sql
-- Total de eventos
SELECT COUNT(*) FROM usage_events;

-- Eventos por usuario
SELECT username, COUNT(*) as total
FROM usage_events
GROUP BY username
ORDER BY total DESC;

-- Eventos por día
SELECT DATE(timestamp) as fecha, COUNT(*) as eventos
FROM usage_events
GROUP BY DATE(timestamp)
ORDER BY fecha DESC;

-- Últimos 10 eventos
SELECT timestamp, username, event
FROM usage_events
ORDER BY timestamp DESC
LIMIT 10;

-- Usuarios únicos
SELECT DISTINCT username FROM usage_events;
```

---

## Troubleshooting

### Error: "No module named 'psycopg2'"

```bash
pip install psycopg2-binary
```

### Error: "Could not connect to PostgreSQL"

**Verificar:**
1. ✅ PostgreSQL está corriendo:
   ```bash
   pg_isready -h tu-host -p 5432
   ```

2. ✅ Credenciales correctas en `.env`:
   ```bash
   cat .env | grep POSTGRES
   ```

3. ✅ Firewall permite conexión:
   ```bash
   telnet tu-host 5432
   # O con nc:
   nc -zv tu-host 5432
   ```

4. ✅ Base de datos existe:
   ```bash
   psql -h host -U user -l
   ```

### Error: "Permission denied for table usage_events"

El usuario no tiene permisos:

```sql
-- Conectarse como admin
psql -h host -U postgres -d database

-- Dar permisos
GRANT ALL PRIVILEGES ON TABLE usage_events TO app_user;
GRANT USAGE, SELECT ON SEQUENCE usage_events_id_seq TO app_user;
```

### Dashboard no muestra datos

**Verificar:**

1. ✅ Hay datos en la BD:
   ```sql
   SELECT COUNT(*) FROM usage_events;
   ```

2. ✅ Usuario tiene permisos de admin:
   ```bash
   # En .env, verificar que tu usuario está en:
   AUTH_ADMIN_USERS=se43617,se46958,se42998,se41714,se48659,se48762,ry40860,nicolas.ursino
   ```

3. ✅ LOG_ENABLED está en true:
   ```bash
   cat .env | grep LOG_ENABLED
   ```

4. ✅ Backend correcto:
   ```bash
   cat .env | grep LOG_BACKEND
   ```

### SQLite: "Database is locked"

Alta concurrencia en SQLite. Solución:

**Opción 1:** Migrar a PostgreSQL (recomendado)

**Opción 2:** Configurar timeout:
```python
# En shared/usage_logger.py, línea ~93
conn = sqlite3.connect(str(self.db_path), timeout=30.0)
```

### Logs se pierden al reiniciar (Streamlit Cloud)

Streamlit Cloud tiene sistema efímero. Soluciones:

1. **Usar PostgreSQL externo** (Supabase, Neon) - **RECOMENDADO**
2. Usar servicio de storage persistente (AWS S3, Azure Blob)
3. Aceptar pérdida de datos (solo para demo)

---

## 🎯 Resumen: Qué Hacer Ahora

### Para la presentación (mantener como está):
```bash
# .env
AUTH_BACKEND=local
LOG_BACKEND=file
```

### Cuando te aprueben para cloud:

**Opción rápida (SQLite):**
1. Cambiar `.env`:
   ```bash
   LOG_BACKEND=sqlite
   LOG_SQLITE_PATH=data/usage.db
   ```
2. Deploy en Streamlit Cloud
3. Listo en 5 minutos

**Opción robusta (PostgreSQL):**
1. Crear cuenta en Supabase (gratis)
2. Copiar credenciales
3. Actualizar `.env` con credenciales PostgreSQL
4. Migrar logs existentes: `python scripts/migrate_logs_to_postgres.py`
5. Deploy
6. Listo para producción

---

## 📞 Soporte

Si tenés problemas:

1. **Revisar logs de la app:**
   ```bash
   streamlit run main.py --logger.level=debug
   ```

2. **Verificar conexión a BD:**
   ```bash
   # PostgreSQL
   psql -h host -U user -d db -c "SELECT 1;"
   
   # SQLite
   sqlite3 data/usage.db ".tables"
   ```

3. **Contactar al equipo de BI/IT de YPF**

---

**Última actualización:** Abril 2026  
**Versión:** 1.0  
**Autor:** Claude (YPF BI Team)

---

## 📎 Anexo: Comandos Rápidos

### Verificar configuración actual
```bash
cat .env | grep -E "(AUTH_BACKEND|LOG_BACKEND)"
```

### Testear conexión PostgreSQL
```bash
psql -h $LOG_POSTGRES_HOST -U $LOG_POSTGRES_USER -d $LOG_POSTGRES_DB -c "SELECT version();"
```

### Ver logs de la app
```bash
streamlit run main.py 2>&1 | tee app.log
```

### Backup de logs SQLite
```bash
sqlite3 data/usage.db ".backup backup_$(date +%Y%m%d).db"
```

### Backup de logs PostgreSQL
```bash
pg_dump -h host -U user -d db -t usage_events > backup_$(date +%Y%m%d).sql
```

---

**¡Todo listo para migrar cuando te den el OK! 🚀**

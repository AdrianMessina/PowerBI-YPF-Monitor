# Guía de Deployment Cloud - YPF BI Monitor

Esta guía explica cómo desplegar YPF BI Monitor en diferentes entornos cloud, con enfoque especial en integración con Cloudera y sistemas corporativos de YPF.

---

## Tabla de Contenidos

1. [Configuración General](#configuración-general)
2. [Deployment en Streamlit Cloud](#deployment-en-streamlit-cloud)
3. [Deployment en Cloudera](#deployment-en-cloudera)
4. [Configuración de Autenticación](#configuración-de-autenticación)
5. [Configuración de Logging](#configuración-de-logging)
6. [Migraciones y Actualizaciones](#migraciones-y-actualizaciones)

---

## Configuración General

### Requisitos Previos

- Python 3.8+
- Acceso a sistema de autenticación corporativo (LDAP/AD, Cloudera SSO, etc.)
- Base de datos PostgreSQL (recomendado para producción) o SQLite (para pruebas)

### Dependencias Adicionales para Cloud

Agregar a `requirements.txt`:

```txt
# Para autenticación LDAP
ldap3==2.9.1

# Para PostgreSQL
psycopg2-binary==2.9.9

# Para OAuth (opcional)
requests-oauthlib==1.3.1
```

---

## Deployment en Streamlit Cloud

### 1. Preparar el Repositorio

Asegurar que el repositorio tenga:
- ✅ `requirements.txt` completo con todas las dependencias
- ✅ `.gitignore` que excluya `.env` y archivos sensibles
- ✅ `README.md` con instrucciones básicas

### 2. Configurar Secrets en Streamlit Cloud

En la interfaz de Streamlit Cloud, ir a **Settings > Secrets** y agregar:

```toml
# Autenticación
AUTH_BACKEND = "local"
AUTH_WHITELIST = ""
AUTH_ADMIN_USERS = "se43617,se46958,se42998,se41714,se48659,se48762,ry40860,nicolas.ursino"

# Logging con SQLite (más simple para Streamlit Cloud)
LOG_BACKEND = "sqlite"
LOG_SQLITE_PATH = "/tmp/usage.db"
LOG_ENABLED = "true"

# Deployment
DEPLOYMENT_ENV = "cloud"
APP_BASE_URL = "https://your-app.streamlit.app"
```

### 3. Deploy

1. Conectar repositorio de GitHub a Streamlit Cloud
2. Seleccionar `main.py` como archivo principal
3. Configurar Python 3.9+
4. Deploy!

### Limitaciones de Streamlit Cloud

⚠️ **Importante:** Streamlit Cloud tiene sistema de archivos efímero. Para persistencia:
- Usar `LOG_BACKEND=sqlite` con ruta en `/tmp/` (se pierde al reiniciar)
- O mejor: usar PostgreSQL externo (recomendado)

---

## Deployment en Cloudera

### 1. Arquitectura Recomendada

```
┌─────────────────────────────────────┐
│  Cloudera Data Platform (CDP)      │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  YPF BI Monitor (Streamlit)   │ │
│  │  - Puerto: 8501               │ │
│  │  - Auth: Cloudera SSO         │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  PostgreSQL Database          │ │
│  │  - Logs de uso                │ │
│  │  - Configuraciones            │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  LDAP/Active Directory        │ │
│  │  - Autenticación usuarios     │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

### 2. Configurar Variables de Entorno en Cloudera

Crear archivo `.env` en el servidor:

```bash
# Autenticación con Cloudera
AUTH_BACKEND=cloudera

AUTH_ADMIN_USERS=se43617,se46958,se42998,se41714,se48659,se48762,ry40860,nicolas.ursino

# Cloudera SSO
CLOUDERA_AUTH_ENDPOINT=https://cloudera.ypf.com/api/v1/auth
CLOUDERA_VERIFY_SSL=true

# Logging con PostgreSQL
LOG_BACKEND=postgres
LOG_POSTGRES_HOST=postgres.ypf.com
LOG_POSTGRES_PORT=5432
LOG_POSTGRES_DB=ypf_bi_monitor
LOG_POSTGRES_USER=app_user
LOG_POSTGRES_PASSWORD=<secret>
LOG_POSTGRES_TABLE=usage_events

# Deployment
DEPLOYMENT_ENV=cloudera
APP_BASE_URL=https://bi-monitor.ypf.com
```

### 3. Inicializar Base de Datos PostgreSQL

```sql
-- Conectarse a PostgreSQL
psql -h postgres.ypf.com -U postgres -d ypf_bi_monitor

-- Crear usuario de aplicación
CREATE USER app_user WITH PASSWORD 'secure_password';

-- Crear base de datos
CREATE DATABASE ypf_bi_monitor OWNER app_user;

-- Conectarse a la BD
\c ypf_bi_monitor

-- La tabla se crea automáticamente al iniciar la app
-- Pero se puede crear manualmente:
CREATE TABLE usage_events (
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

CREATE INDEX idx_usage_events_timestamp ON usage_events(timestamp);
CREATE INDEX idx_usage_events_username ON usage_events(username);
CREATE INDEX idx_usage_events_event ON usage_events(event);

-- Dar permisos
GRANT ALL PRIVILEGES ON TABLE usage_events TO app_user;
GRANT USAGE, SELECT ON SEQUENCE usage_events_id_seq TO app_user;
```

### 4. Instalar y Ejecutar en Cloudera

```bash
# Clonar repositorio
cd /opt/apps
git clone https://github.com/your-org/ypf-bi-monitor.git
cd ypf-bi-monitor

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar y configurar .env
cp .env.example .env
nano .env  # Editar con valores de producción

# Ejecutar
streamlit run main.py --server.port 8501 --server.address 0.0.0.0
```

### 5. Configurar como Servicio Systemd

Crear `/etc/systemd/system/ypf-bi-monitor.service`:

```ini
[Unit]
Description=YPF BI Monitor
After=network.target postgresql.service

[Service]
Type=simple
User=app_user
WorkingDirectory=/opt/apps/ypf-bi-monitor
Environment="PATH=/opt/apps/ypf-bi-monitor/venv/bin"
EnvironmentFile=/opt/apps/ypf-bi-monitor/.env
ExecStart=/opt/apps/ypf-bi-monitor/venv/bin/streamlit run main.py --server.port 8501 --server.address 0.0.0.0
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Habilitar y arrancar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ypf-bi-monitor
sudo systemctl start ypf-bi-monitor
sudo systemctl status ypf-bi-monitor
```

### 6. Configurar Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name bi-monitor.ypf.com;

    # Redirigir a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name bi-monitor.ypf.com;

    ssl_certificate /etc/ssl/certs/ypf.crt;
    ssl_certificate_key /etc/ssl/private/ypf.key;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

---

## Configuración de Autenticación

### Opción 1: Local (Desarrollo)

```bash
AUTH_BACKEND=local

AUTH_ADMIN_USERS=se43617,se46958,se42998,se41714,se48659,se48762,ry40860,nicolas.ursino
```

**Funcionamiento:** Detecta usuario Windows automáticamente, valida contra whitelist.

### Opción 2: LDAP/Active Directory

```bash
AUTH_BACKEND=ldap

AUTH_ADMIN_USERS=se43617,se46958,se42998,se41714,se48659,se48762,ry40860,nicolas.ursino

# Configuración LDAP
LDAP_SERVER=ldap.ypf.com
LDAP_PORT=389
LDAP_BASE_DN=dc=grupo,dc=ypf,dc=com
LDAP_USER_DN_TEMPLATE=cn={username},{base_dn}
LDAP_USE_SSL=false
```

**Funcionamiento:** Usuario ingresa credenciales, se validan contra LDAP corporativo.

### Opción 3: Cloudera SSO

```bash
AUTH_BACKEND=cloudera

AUTH_ADMIN_USERS=se43617,se46958,se42998,se41714,se48659,se48762,ry40860,nicolas.ursino

# Configuración Cloudera
CLOUDERA_AUTH_ENDPOINT=https://cloudera.ypf.com/api/v1/auth
CLOUDERA_VERIFY_SSL=true
```

**Funcionamiento:** Usuario ingresa credenciales, se validan contra API de Cloudera.

### Opción 4: Sin Autenticación (Solo Desarrollo)

```bash
AUTH_BACKEND=none
# NUNCA usar en producción
```

---

## Configuración de Logging

### Opción 1: Archivos Locales (Desarrollo)

```bash
LOG_BACKEND=file
LOG_FILE_DIR=  # Usa logs/ por default
LOG_ENABLED=true
```

**Pros:** Simple, no requiere BD  
**Contras:** No escalable, se pierde en restart (cloud efímero)

### Opción 2: SQLite (Cloud Simple)

```bash
LOG_BACKEND=sqlite
LOG_SQLITE_PATH=/tmp/usage.db  # En Streamlit Cloud
# O en servidor persistente:
# LOG_SQLITE_PATH=/opt/apps/ypf-bi-monitor/data/usage.db
LOG_ENABLED=true
```

**Pros:** Simple, sin servidor de BD  
**Contras:** No ideal para alta concurrencia

### Opción 3: PostgreSQL (Producción)

```bash
LOG_BACKEND=postgres
LOG_POSTGRES_HOST=postgres.ypf.com
LOG_POSTGRES_PORT=5432
LOG_POSTGRES_DB=ypf_bi_monitor
LOG_POSTGRES_USER=app_user
LOG_POSTGRES_PASSWORD=<secret>
LOG_POSTGRES_TABLE=usage_events
LOG_ENABLED=true
```

**Pros:** Escalable, persistente, soporta concurrencia  
**Contras:** Requiere servidor PostgreSQL

**⭐ Recomendado para producción en Cloudera**

---

## Migraciones y Actualizaciones

### Migrar de File a PostgreSQL

```python
# Script de migración: migrate_logs.py
import json
from pathlib import Path
from shared.usage_logger import LogConfig, PostgresLogBackend

# Configurar PostgreSQL
config = LogConfig()
config.backend = "postgres"
config.postgres_host = "postgres.ypf.com"
# ... resto de config

backend = PostgresLogBackend(config)

# Leer archivos JSONL
logs_dir = Path("logs")
for log_file in logs_dir.glob("usage_*.jsonl"):
    with open(log_file, 'r') as f:
        for line in f:
            if line.strip():
                event = json.loads(line)
                backend.log_event(event)

print("Migración completada!")
```

Ejecutar:

```bash
python migrate_logs.py
```

### Actualizar Variables de Entorno Sin Downtime

1. Editar `.env`
2. Reiniciar aplicación:

```bash
# Con systemd
sudo systemctl restart ypf-bi-monitor

# Manual
pkill -f streamlit
streamlit run main.py &
```

---

## Monitoreo y Troubleshooting

### Ver Logs de Aplicación

```bash
# Con systemd
journalctl -u ypf-bi-monitor -f

# Manual
tail -f /var/log/ypf-bi-monitor.log
```

### Verificar Conectividad PostgreSQL

```bash
psql -h postgres.ypf.com -U app_user -d ypf_bi_monitor -c "SELECT COUNT(*) FROM usage_events;"
```

### Verificar Autenticación LDAP

```bash
ldapsearch -x -H ldap://ldap.ypf.com -b "dc=grupo,dc=ypf,dc=com" -D "cn=testuser,dc=grupo,dc=ypf,dc=com" -W
```

### Health Check

Crear endpoint `/health`:

```python
# En main.py
import streamlit as st

# Health check (accesible sin autenticación)
if st.query_params.get("health") == "check":
    st.write("OK")
    st.stop()
```

Acceso: `https://bi-monitor.ypf.com/?health=check`

---

## Checklist de Deployment

### Pre-Deployment

- [ ] `.env` configurado con valores de producción
- [ ] PostgreSQL configurado y accesible
- [ ] LDAP/Cloudera auth testeado
- [ ] Whitelist de usuarios actualizada
- [ ] Dependencias instaladas (`requirements.txt`)
- [ ] Certificados SSL configurados

### Post-Deployment

- [ ] Health check funciona
- [ ] Usuarios pueden autenticarse
- [ ] Logs se guardan correctamente en PostgreSQL
- [ ] Dashboard de usage muestra datos
- [ ] Reverse proxy funciona (HTTPS)
- [ ] Servicio systemd habilitado
- [ ] Monitoreo configurado

---

## Soporte

Para preguntas o problemas:

1. Revisar logs: `journalctl -u ypf-bi-monitor -f`
2. Verificar configuración: `.env`
3. Contactar al equipo de desarrollo de BI

---

## Apéndice: Configuraciones de Ejemplo

### Desarrollo Local

```bash
AUTH_BACKEND=local
AUTH_DEV_MODE=true
LOG_BACKEND=file
LOG_ENABLED=true
```

### Staging (Pre-producción)

```bash
AUTH_BACKEND=ldap

AUTH_ADMIN_USERS=se43617,se46958,se42998,se41714,se48659,se48762,ry40860,nicolas.ursino
LDAP_SERVER=ldap-staging.ypf.com
LOG_BACKEND=sqlite
LOG_SQLITE_PATH=/opt/apps/staging/data/usage.db
```

### Producción Cloudera

```bash
AUTH_BACKEND=cloudera

AUTH_ADMIN_USERS=se43617,se46958,se42998,se41714,se48659,se48762,ry40860,nicolas.ursino
CLOUDERA_AUTH_ENDPOINT=https://cloudera.ypf.com/api/v1/auth
LOG_BACKEND=postgres
LOG_POSTGRES_HOST=postgres.ypf.com
LOG_POSTGRES_DB=ypf_bi_monitor
DEPLOYMENT_ENV=cloudera
```

---

**Última actualización:** Abril 2026  
**Versión:** 1.0

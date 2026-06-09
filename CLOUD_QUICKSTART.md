# Quick Start - Cloud Deployment

Guía rápida para desplegar YPF BI Monitor en la nube (Cloudera o Streamlit Cloud).

---

## ⚡ TL;DR - Deployment en 5 minutos

### 1. Clonar repositorio

```bash
git clone https://github.com/your-org/ypf-bi-monitor.git
cd ypf-bi-monitor
```

### 2. Instalar dependencias

```bash
# Para cloud con PostgreSQL y LDAP
pip install -r requirements-cloud.txt

# Solo local (sin PostgreSQL/LDAP)
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
# Copiar ejemplo
cp .env.example .env

# Editar con tus credenciales
nano .env
```

**Configuración mínima para cloud:**

```bash
# Autenticación
AUTH_BACKEND=local  # o ldap, cloudera

AUTH_ADMIN_USERS=se43617,se46958,se42998,se41714,se48659,se48762,ry40860,nicolas.ursino

# Logging con PostgreSQL (recomendado cloud)
LOG_BACKEND=postgres
LOG_POSTGRES_HOST=tu-servidor-postgres.com
LOG_POSTGRES_PORT=5432
LOG_POSTGRES_DB=ypf_bi_monitor
LOG_POSTGRES_USER=app_user
LOG_POSTGRES_PASSWORD=tu_password_seguro

# O SQLite para pruebas rápidas
# LOG_BACKEND=sqlite
# LOG_SQLITE_PATH=/tmp/usage.db
```

### 4. Ejecutar

```bash
streamlit run main.py
```

Listo! 🚀

---

## 📋 Configuraciones por Ambiente

### Desarrollo Local (sin PostgreSQL)

```bash
AUTH_BACKEND=local
AUTH_DEV_MODE=true
LOG_BACKEND=file
```

### Staging / Testing

```bash
AUTH_BACKEND=local

LOG_BACKEND=sqlite
LOG_SQLITE_PATH=/tmp/usage.db
```

### Producción (Cloudera)

```bash
AUTH_BACKEND=cloudera

AUTH_ADMIN_USERS=se43617,se46958,se42998,se41714,se48659,se48762,ry40860,nicolas.ursino
CLOUDERA_AUTH_ENDPOINT=https://cloudera.ypf.com/api/v1/auth
LOG_BACKEND=postgres
LOG_POSTGRES_HOST=postgres.ypf.com
LOG_POSTGRES_DB=ypf_bi_monitor
```

---

## 🗄️ Setup PostgreSQL

### Opción 1: PostgreSQL Local (Testing)

```bash
# Instalar PostgreSQL (Ubuntu/Debian)
sudo apt install postgresql postgresql-contrib

# Crear base de datos
sudo -u postgres psql
CREATE DATABASE ypf_bi_monitor;
CREATE USER app_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE ypf_bi_monitor TO app_user;
\q
```

### Opción 2: PostgreSQL Cloud

Usar servicio managed:
- **AWS RDS:** PostgreSQL 14+
- **Azure Database:** PostgreSQL
- **Google Cloud SQL:** PostgreSQL

Obtener credenciales y configurar en `.env`.

---

## 🔐 Setup Autenticación

### LDAP/Active Directory

```bash
AUTH_BACKEND=ldap
LDAP_SERVER=ldap.ypf.com
LDAP_PORT=389
LDAP_BASE_DN=dc=grupo,dc=ypf,dc=com
LDAP_USER_DN_TEMPLATE=cn={username},{base_dn}
```

**Verificar conectividad:**

```bash
ldapsearch -x -H ldap://ldap.ypf.com -b "dc=grupo,dc=ypf,dc=com"
```

### Cloudera SSO

```bash
AUTH_BACKEND=cloudera
CLOUDERA_AUTH_ENDPOINT=https://cloudera.ypf.com/api/v1/auth
CLOUDERA_VERIFY_SSL=true
```

---

## 📦 Migrar Logs Existentes a PostgreSQL

Si ya tienes logs en archivos JSONL y quieres migrar a PostgreSQL:

```bash
# 1. Configurar PostgreSQL en .env
nano .env

# 2. Ejecutar script de migración
python scripts/migrate_logs_to_postgres.py

# 3. Verificar migración
psql -h tu-postgres -U app_user -d ypf_bi_monitor \
  -c "SELECT COUNT(*) FROM usage_events;"
```

---

## 🐳 Deployment con Docker (Opcional)

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Copiar archivos
COPY requirements-cloud.txt .
RUN pip install --no-cache-dir -r requirements-cloud.txt

COPY . .

# Exponer puerto Streamlit
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Ejecutar app
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Docker Compose con PostgreSQL

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: ypf_bi_monitor
      POSTGRES_USER: app_user
      POSTGRES_PASSWORD: password
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  app:
    build: .
    environment:
      - AUTH_BACKEND=local
      - 
      - LOG_BACKEND=postgres
      - LOG_POSTGRES_HOST=postgres
      - LOG_POSTGRES_DB=ypf_bi_monitor
      - LOG_POSTGRES_USER=app_user
      - LOG_POSTGRES_PASSWORD=password
    ports:
      - "8501:8501"
    depends_on:
      - postgres

volumes:
  pgdata:
```

**Ejecutar:**

```bash
docker-compose up -d
```

---

## ✅ Checklist Pre-Deployment

- [ ] `.env` configurado correctamente
- [ ] PostgreSQL accesible desde el servidor
- [ ] Whitelist de usuarios actualizada
- [ ] Credenciales LDAP/Cloudera testeadas
- [ ] Dependencias instaladas (`requirements-cloud.txt`)
- [ ] Health check funciona: `curl http://localhost:8501/_stcore/health`

---

## 🆘 Troubleshooting

### Error: "LDAP not configured"

```bash
pip install ldap3
```

### Error: "PostgreSQL connection failed"

Verificar:
1. PostgreSQL está corriendo: `pg_isready -h host`
2. Credenciales correctas en `.env`
3. Firewall permite conexión al puerto 5432

### Error: "Authentication failed"

- Verificar que el usuario esté en `AUTH_WHITELIST`
- Si usa LDAP, verificar `LDAP_USER_DN_TEMPLATE`
- Ver logs: `streamlit run main.py --logger.level=debug`

---

## 📚 Documentación Completa

Para guía detallada, ver:
- [CLOUD_DEPLOYMENT.md](./CLOUD_DEPLOYMENT.md) - Guía completa de deployment
- [README.md](./README.md) - Documentación general
- [INSTALL.md](./INSTALL.md) - Instalación local

---

## 🚀 Ready to Deploy!

Una vez configurado, la app estará lista para:
- ✅ Autenticación corporativa (LDAP/Cloudera)
- ✅ Logging centralizado (PostgreSQL)
- ✅ Dashboard multi-usuario
- ✅ Alta disponibilidad

**URL de acceso:** `https://tu-servidor:8501`

---

**¿Preguntas?** Contactar al equipo de BI de YPF.

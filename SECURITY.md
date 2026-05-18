# 🔒 Guía de Seguridad - YPF BI Monitor

**Versión:** 1.0  
**Fecha:** 2026-05-18  
**Audiencia:** Desarrolladores y Administradores

---

## 🎯 Objetivo

Este documento establece las prácticas de seguridad para proteger información sensible antes de subir código a GitHub o deployar en ambientes de producción.

---

## ⚠️ Información Sensible (NO subir a GitHub)

### 🔴 Crítico - NUNCA subir:

- **Contraseñas** (admin passwords, DB passwords, etc.)
- **API Keys y Tokens** (OpenAI, Azure, AWS, etc.)
- **Claves privadas** (SSH keys, SSL certificates)
- **Credenciales de Base de Datos** (usuarios, passwords, hosts)
- **Secretos OAuth** (client secrets, refresh tokens)

### 🟠 Alto Riesgo - Evitar subir:

- **Códigos de usuario YPF** (se43617, ry40860, etc.)
- **Nombres completos de empleados** (excepto en AUTHORS o CONTRIBUTORS)
- **Emails corporativos** (@grupo.ypf.com)
- **IPs internas** (192.168.x.x, 10.x.x.x)
- **Rutas de red internas** (\\servidor\carpeta)

### 🟡 Precaución - Revisar contexto:

- **Nombres de servidores** (puede ser OK si es público o genérico)
- **Nombres de bases de datos** (OK si es genérico como "ypf_bi_monitor")
- **URLs públicas** (OK si son del dominio público)

---

## ✅ Archivos de Configuración

### Archivo `.env` (NUNCA subir - ya está en .gitignore)

Contiene valores **reales** para tu ambiente local o producción:

```env
# .env - REAL VALUES (NO SUBIR A GITHUB)
AUTH_ADMIN_USERS=se43617,se46958,se42998
YPF_BI_ADMIN_PASSWORD=mi_clave_secreta_real
LOG_POSTGRES_PASSWORD=db_password_real
```

✅ **Protección:** Ya está en `.gitignore`  
✅ **Ubicación:** Solo en máquina local o servidor de producción  
❌ **NUNCA:** hacer `git add .env`

---

### Archivo `.env.example` (SÍ subir a GitHub)

Plantilla **pública** con valores de ejemplo genéricos:

```env
# .env.example - TEMPLATE (OK PARA GITHUB)
AUTH_ADMIN_USERS=
YPF_BI_ADMIN_PASSWORD=cambiar_esta_clave
LOG_POSTGRES_PASSWORD=your_password
```

✅ **OK para GitHub:** Valores de ejemplo, no reales  
✅ **Propósito:** Mostrar qué variables se necesitan configurar  
✅ **Usuarios:** Copian este archivo como `.env` y completan valores reales

---

### Archivo `.env.ypf.example` (NUNCA subir - en .gitignore)

Plantilla **interna YPF** con valores reales para el equipo:

```env
# .env.ypf.example - INTERNAL YPF ONLY (NO SUBIR A GITHUB)
AUTH_ADMIN_USERS=se43617,se46958,se42998,se41714,se48659,se48762,ry40860,nicolas.ursino
```

✅ **Protección:** Agregado a `.gitignore`  
✅ **Propósito:** Compartir config real dentro del equipo YPF  
✅ **Distribución:** Solo vía canales internos (SharePoint, Teams, email corporativo)  
❌ **NUNCA:** Subir a GitHub público

---

## 🛠️ Herramientas de Verificación

### Script de Seguridad Pre-Commit

Antes de hacer commit, ejecutar:

```bash
python scripts/verify_security.py
```

Este script verifica:
- ✅ `.gitignore` tiene todas las entradas necesarias
- ✅ `.env.example` no tiene valores reales (usuarios, passwords)
- ✅ No hay contraseñas hardcodeadas en el código
- ✅ No hay API keys expuestas
- ✅ No hay usuarios YPF en archivos públicos

**Salida esperada:**

```
🔍 Escaneando archivos en busca de información sensible...

=================================================================
📊 REPORTE DE SEGURIDAD
=================================================================

Total de issues encontrados: 0
  🔴 Críticos: 0
  🟠 Altos:    0
  🟡 Medios:   0
  🟢 Bajos:    0

=================================================================
✅ TODO OK - SEGURO PARA COMMIT A GITHUB
=================================================================
```

**Si hay problemas:**

```
🔴 [CRITICAL] .env.example:32
   Tipo: usuario_ypf_en_example
   Contenido: AUTH_ADMIN_USERS=se43617,se46958,...

⚠️  NO HACER COMMIT HASTA RESOLVER LOS ISSUES CRÍTICOS Y ALTOS
```

---

## 📋 Checklist Pre-GitHub

Antes de hacer `git push` por primera vez:

### 1. Verificar .gitignore
- [ ] `.env` está en `.gitignore`
- [ ] `.env.ypf.example` está en `.gitignore`
- [ ] `logs/` está en `.gitignore`
- [ ] `.streamlit/secrets.toml` está en `.gitignore`

### 2. Limpiar .env.example
- [ ] No contiene códigos de usuario YPF (se43617, etc.)
- [ ] No contiene emails corporativos reales
- [ ] No contiene contraseñas reales
- [ ] Valores están vacíos o con placeholders (`your_password`, `changeme`, etc.)

### 3. Verificar código fuente
- [ ] No hay contraseñas hardcodeadas en `.py` files
- [ ] No hay API keys en el código
- [ ] No hay IPs internas en configuraciones
- [ ] Variables sensibles vienen de `os.getenv()`, no hardcoded

### 4. Ejecutar verificación
```bash
python scripts/verify_security.py
```
- [ ] Reporte muestra 0 issues críticos
- [ ] Reporte muestra 0 issues altos

### 5. Revisar cambios manualmente
```bash
git diff
```
- [ ] Revisar cada archivo modificado
- [ ] Verificar que no hay datos sensibles accidentales

### 6. Commit seguro
```bash
git add .
git commit -m "Initial commit - YPF BI Monitor"
git push origin main
```

---

## 🔐 Configuración en Producción

### Opción 1: Variables de Entorno del Sistema (Recomendado)

En Cloudera / Linux / Cloud:

```bash
# Configurar en el sistema operativo
export AUTH_ADMIN_USERS="se43617,se46958,se42998"
export LOG_POSTGRES_PASSWORD="db_password_prod"

# La app las lee automáticamente
streamlit run main.py
```

✅ **Ventajas:**
- Más seguro (no están en archivos)
- Fácil de cambiar sin modificar código
- Compatible con Cloudera, Docker, Kubernetes

### Opción 2: Archivo .env Local (Desarrollo)

```bash
# Copiar plantilla
cp .env.ypf.example .env

# Editar con valores reales
nano .env

# Ejecutar app (lee .env automáticamente)
streamlit run main.py
```

✅ **Ventajas:**
- Fácil para desarrollo local
- No requiere configurar sistema operativo

❌ **Desventajas:**
- Menos seguro (archivo en disco)
- Riesgo de commitear accidentalmente

### Opción 3: Secrets de Streamlit Cloud

Si deployando en Streamlit Cloud:

```toml
# .streamlit/secrets.toml (ya está en .gitignore)
AUTH_ADMIN_USERS = "se43617,se46958"
LOG_POSTGRES_PASSWORD = "password"
```

✅ **Ventajas:**
- Integración nativa con Streamlit Cloud
- Encriptado en tránsito

---

## 🚨 Qué Hacer si Expusiste un Secreto

### Si el secreto NO fue pusheado a GitHub:

1. **Remover del archivo**
   ```bash
   # Editar archivo y quitar el secreto
   nano archivo_con_secreto.py
   ```

2. **No hacer commit**
   ```bash
   git reset archivo_con_secreto.py
   ```

3. **Verificar**
   ```bash
   python scripts/verify_security.py
   ```

---

### Si el secreto YA fue pusheado a GitHub:

#### Paso 1: CAMBIAR EL SECRETO INMEDIATAMENTE

- Contraseña → Cambiarla en el sistema
- API Key → Regenerarla/revocarla
- Token → Invalidarlo

#### Paso 2: Eliminar del historial de Git

```bash
# Usar BFG Repo-Cleaner o git-filter-repo
git filter-repo --invert-paths --path archivo_con_secreto.env

# Force push (¡CUIDADO!)
git push --force origin main
```

⚠️ **Advertencia:** `git push --force` puede afectar a otros colaboradores.

#### Paso 3: Notificar al equipo

- Informar a IT Security de YPF
- Documentar el incidente
- Verificar logs de acceso

#### Paso 4: Prevenir recurrencia

- Configurar GitHub secret scanning
- Usar pre-commit hooks
- Capacitar al equipo

---

## 🔍 Revisión de Código (Code Review)

Al revisar Pull Requests, verificar:

### Checklist de Reviewer:

- [ ] No hay contraseñas hardcodeadas
- [ ] No hay API keys en el código
- [ ] Archivos `.env*` no fueron modificados (excepto `.env.example`)
- [ ] Variables sensibles usan `os.getenv()`
- [ ] No hay comentarios con TODOs de seguridad sin resolver
- [ ] Se agregaron nuevas entradas a `.gitignore` si es necesario

### Red Flags:

❌ `password = "mi_clave_secreta"`  
❌ `api_key = "sk-abc123xyz"`  
❌ `users = ["se43617", "se46958"]` (hardcoded)  
❌ `git add .env` en instrucciones  

✅ `password = os.getenv('DB_PASSWORD')`  
✅ `api_key = os.getenv('OPENAI_API_KEY')`  
✅ `users = os.getenv('AUTH_ADMIN_USERS', '').split(',')`  
✅ `cp .env.example .env` en instrucciones  

---

## 📞 Contacto de Seguridad

**Para reportar issues de seguridad:**

- **Equipo:** IT Analytics - YPF S.A.
- **Email:** [Contacto interno YPF]
- **No reportar issues de seguridad en GitHub Issues público**

**Para consultas generales:**
- Ver [README.md](README.md)
- Crear Issue en GitHub (si no es sensible)

---

## 📚 Referencias

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [.gitignore Best Practices](https://github.com/github/gitignore)
- [Twelve-Factor App - Config](https://12factor.net/config)

---

## ✅ Resumen

### DO's ✅

- ✅ Usar variables de entorno para secretos
- ✅ Mantener `.env` en `.gitignore`
- ✅ Usar valores de ejemplo en `.env.example`
- ✅ Ejecutar `verify_security.py` antes de commit
- ✅ Compartir config real solo por canales internos
- ✅ Cambiar secretos si se exponen

### DON'Ts ❌

- ❌ Hardcodear contraseñas en código
- ❌ Subir `.env` a GitHub
- ❌ Poner usuarios reales en `.env.example`
- ❌ Commitear API keys
- ❌ Ignorar warnings del security scanner
- ❌ Compartir secretos en Slack/email no cifrado

---

**Desarrollado con 🔒 seguridad por IT Analytics - YPF S.A.**  
**Última actualización:** 2026-05-18

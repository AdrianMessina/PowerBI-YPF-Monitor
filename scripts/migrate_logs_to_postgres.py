#!/usr/bin/env python3
"""
Script de migración de logs desde archivos JSONL a PostgreSQL

Uso:
    python scripts/migrate_logs_to_postgres.py

Configuración:
    Las credenciales de PostgreSQL se leen desde variables de entorno
    o del archivo .env en la raíz del proyecto
"""

import sys
import json
from pathlib import Path

# Agregar raíz del proyecto al path para importar módulos
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.usage_logger import LogConfig, PostgresLogBackend


def migrate_logs():
    """Migrar logs desde archivos JSONL a PostgreSQL"""

    # Configurar backend PostgreSQL
    print("🔧 Configurando conexión a PostgreSQL...")
    config = LogConfig()

    # Verificar que esté configurado para PostgreSQL
    if config.backend.value != "postgres":
        print("⚠️  LOG_BACKEND debe estar configurado como 'postgres' en .env")
        print("   Configurando manualmente para migración...")

    # Forzar PostgreSQL para migración
    from shared.usage_logger import LogBackend
    config.backend = LogBackend.POSTGRES

    if not config.postgres_host or not config.postgres_db:
        print("❌ Error: Configuración de PostgreSQL incompleta")
        print("   Verificar LOG_POSTGRES_* en .env")
        return False

    print(f"   Host: {config.postgres_host}")
    print(f"   Database: {config.postgres_db}")
    print(f"   Table: {config.postgres_table}")

    try:
        backend = PostgresLogBackend(config)
        print("✅ Conexión exitosa a PostgreSQL")
    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")
        return False

    # Buscar archivos JSONL
    logs_dir = project_root / "logs"
    if not logs_dir.exists():
        print(f"❌ No se encontró directorio de logs: {logs_dir}")
        return False

    log_files = sorted(logs_dir.glob("usage_*.jsonl"))
    if not log_files:
        print("❌ No se encontraron archivos de logs (usage_*.jsonl)")
        return False

    print(f"\n📁 Encontrados {len(log_files)} archivos de logs")

    # Migrar cada archivo
    total_events = 0
    migrated_events = 0
    errors = 0

    for log_file in log_files:
        print(f"\n📄 Procesando: {log_file.name}")
        file_events = 0

        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue

                    total_events += 1

                    try:
                        event = json.loads(line)
                        backend.log_event(event)
                        migrated_events += 1
                        file_events += 1

                        # Progreso cada 100 eventos
                        if file_events % 100 == 0:
                            print(f"   ⏳ Migrados {file_events} eventos...", end='\r')

                    except json.JSONDecodeError as e:
                        print(f"   ⚠️  Línea {line_num}: Error JSON - {e}")
                        errors += 1
                    except Exception as e:
                        print(f"   ⚠️  Línea {line_num}: Error migrando - {e}")
                        errors += 1

            print(f"   ✅ {file_events} eventos migrados")

        except Exception as e:
            print(f"   ❌ Error leyendo archivo: {e}")
            errors += 1

    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE MIGRACIÓN")
    print("="*60)
    print(f"Total eventos encontrados:  {total_events}")
    print(f"Eventos migrados:           {migrated_events}")
    print(f"Errores:                    {errors}")
    print("="*60)

    if migrated_events > 0:
        print("\n✅ Migración completada exitosamente")
        print("\n💡 Próximos pasos:")
        print("   1. Verificar datos en PostgreSQL:")
        print(f"      SELECT COUNT(*) FROM {config.postgres_table};")
        print("   2. Actualizar .env:")
        print("      LOG_BACKEND=postgres")
        print("   3. Reiniciar la aplicación")
        return True
    else:
        print("\n❌ No se migraron eventos")
        return False


if __name__ == "__main__":
    print("="*60)
    print("🚀 MIGRACIÓN DE LOGS A POSTGRESQL")
    print("="*60)
    print()

    # Verificar dependencias
    try:
        import psycopg2
    except ImportError:
        print("❌ Error: psycopg2 no instalado")
        print("   Instalar con: pip install psycopg2-binary")
        sys.exit(1)

    # Ejecutar migración
    try:
        success = migrate_logs()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Migración cancelada por usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

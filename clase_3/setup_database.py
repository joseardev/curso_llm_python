#!/usr/bin/env python3
"""
Script para crear la base de datos PostgreSQL y ejecutar el schema.sql
Automáticamente sin necesidad de psql o Docker.
"""

import psycopg
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Configuración desde .env
POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql://postgres:postgres@localhost:5432/rag_db")
POSTGRES_DB = os.getenv("POSTGRES_DB", "rag_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

def create_database():
    """Crear la base de datos si no existe"""
    print(f"🔧 Intentando conectar a PostgreSQL en {POSTGRES_HOST}:{POSTGRES_PORT}...")
    
    try:
        # Conectar a la base de datos por defecto (postgres) para crear rag_db
        conn = psycopg.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            dbname="postgres"  # Base de datos por defecto
        )
        conn.autocommit = True
        
        with conn.cursor() as cur:
            # Verificar si la base de datos existe
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (POSTGRES_DB,))
            exists = cur.fetchone()
            
            if not exists:
                print(f"📦 Creando base de datos '{POSTGRES_DB}'...")
                cur.execute(f"CREATE DATABASE {POSTGRES_DB}")
                print(f"✅ Base de datos '{POSTGRES_DB}' creada")
            else:
                print(f"✅ Base de datos '{POSTGRES_DB}' ya existe")
        
        conn.close()
        return True
        
    except psycopg.Error as e:
        print(f"❌ Error al crear la base de datos: {e}")
        print(f"   Verifica que PostgreSQL está en ejecución y las credenciales son correctas")
        return False


def execute_schema():
    """Ejecutar el schema.sql en la base de datos"""
    print(f"\n📄 Ejecutando schema.sql en '{POSTGRES_DB}'...")
    
    try:
        conn = psycopg.connect(POSTGRES_URI)
        conn.autocommit = True
        
        # Leer el archivo schema.sql
        schema_path = Path(__file__).parent / "schema.sql"
        if not schema_path.exists():
            print(f"❌ Error: No se encontró {schema_path}")
            return False
        
        with open(schema_path, "r") as f:
            sql = f.read()
        
        # Ejecutar el schema
        with conn.cursor() as cur:
            cur.execute(sql)
        
        print("✅ Schema ejecutado correctamente")
        
        # Verificar que las tablas se crearon
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('documents', 'document_chunks')
                ORDER BY table_name
            """)
            tables = [row[0] for row in cur.fetchall()]
            
            if len(tables) == 2:
                print(f"✅ Tablas creadas: {', '.join(tables)}")
            else:
                print(f"⚠️  Tablas encontradas: {', '.join(tables) if tables else 'Ninguna'}")
        
        conn.close()
        return True
        
    except psycopg.Error as e:
        print(f"❌ Error al ejecutar el schema: {e}")
        return False


def main():
    print("=" * 60)
    print("CONFIGURACIÓN DE LA BASE DE DATOS POSTGRESQL")
    print("=" * 60)
    print(f"URI de conexión: {POSTGRES_URI}")
    print()
    
    # Paso 1: Crear la base de datos
    if not create_database():
        print("\n❌ No se pudo crear la base de datos. Soluciona los errores y vuelve a intentarlo.")
        return
    
    # Paso 2: Ejecutar el schema
    if not execute_schema():
        print("\n❌ No se pudo ejecutar el schema. Soluciona los errores y vuelve a intentarlo.")
        return
    
    print("\n" + "=" * 60)
    print("✅ ¡BASE DE DATOS CONFIGURADA CORRECTAMENTE!")
    print("=" * 60)
    print("\nPuedes ejecutar ahora la ingesta de documentos:")
    print("  .venv\Scripts\python -m clase_3.ingest")


if __name__ == "__main__":
    main()

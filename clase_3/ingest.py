"""
Sistema RAG: Script de ingesta de documentos.

Este script:
1. Escanea el directorio documents/ en busca de archivos .txt
2. Procesa cada documento: lo divide en chunks, genera embeddings y los almacena en PostgreSQL
3. Proporciona información de progreso durante el proceso
"""

import os
from pathlib import Path
from typing import List, Dict, Any
import time

from .rag import process_document, get_connection, ensure_tables_exist
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Configuración
DOCUMENTS_DIR = Path(__file__).resolve().parent / "documents"
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))


def find_text_files(directory: Path) -> List[Path]:
    """
    Encontrar todos los archivos .txt en un directorio.
    
    Args:
        directory: Directorio a escanear
    
    Returns:
        Lista de rutas a archivos .txt
    """
    if not directory.exists():
        raise FileNotFoundError(f"Directorio no encontrado: {directory}")
    
    text_files = []
    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.suffix.lower() == '.txt':
            text_files.append(file_path)
    
    return sorted(text_files)


def verify_database_ready() -> bool:
    """
    Verificar que la base de datos está lista para la ingesta.
    
    Returns:
        True si la base de datos está lista
    """
    try:
        conn = get_connection()
        ready = ensure_tables_exist(conn)
        conn.close()
        return ready
    except Exception as e:
        print(f"Error al verificar la base de datos: {e}")
        return False


def ingest_all_documents(chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> Dict[str, Any]:
    """
    Procesar todos los documentos .txt en el directorio documents/.
    
    Args:
        chunk_size: Tamaño de cada chunk
        overlap: Solapamiento entre chunks
    
    Returns:
        Diccionario con estadísticas del proceso de ingesta
    """
    # Verificar base de datos
    if not verify_database_ready():
        raise RuntimeError(
            "Base de datos no lista. Asegúrate de que: "
            "\n1. PostgreSQL está en ejecución "
            "\n2. Las tablas han sido creadas (ejecuta schema.sql) "
            "\n3. POSTGRES_URI en .env es correcta"
        )
    
    # Encontrar archivos
    documents_dir = DOCUMENTS_DIR
    text_files = find_text_files(documents_dir)
    
    if not text_files:
        print("No se encontraron archivos .txt en el directorio documents/")
        return {"total_files": 0, "processed_files": 0, "total_chunks": 0}
    
    print(f"Encontrados {len(text_files)} archivos .txt para procesar")
    
    stats = {
        "total_files": len(text_files),
        "processed_files": 0,
        "total_chunks": 0,
        "successful_files": 0,
        "failed_files": 0,
        "file_details": []
    }
    
    # Procesar cada archivo
    for i, file_path in enumerate(text_files, 1):
        filename = file_path.name
        print(f"\n[{i}/{len(text_files)}] Procesando: {filename}")
        print(f"  Tamaño del archivo: {file_path.stat().st_size / 1024:.1f} KB")
        
        try:
            start_time = time.time()
            
            # Procesar documento
            file_stats = process_document(file_path, chunk_size, overlap)
            
            elapsed = time.time() - start_time
            
            stats["processed_files"] += 1
            stats["successful_files"] += 1
            stats["total_chunks"] += file_stats["chunks_stored"]
            
            file_stats["processing_time"] = f"{elapsed:.2f}s"
            stats["file_details"].append(file_stats)
            
            print(f"  ✓ Chunks generados: {file_stats['total_chunks']}")
            print(f"  ✓ Chunks almacenados: {file_stats['chunks_processed']}")
            print(f"  ✓ Tiempo: {elapsed:.2f}s")
            
        except Exception as e:
            stats["failed_files"] += 1
            print(f"  ✗ Error procesando {filename}: {e}")
            stats["file_details"].append({
                "filename": filename,
                "error": str(e),
                "chunks_stored": 0
            })
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE INGESTA")
    print("=" * 60)
    print(f"Archivos totales: {stats['total_files']}")
    print(f"Archivos procesados con éxito: {stats['successful_files']}")
    print(f"Archivos fallidos: {stats['failed_files']}")
    print(f"Chunks totales almacenados: {stats['total_chunks']}")
    
    if stats["failed_files"] > 0:
        print(f"\nArchivos con errores:")
        for detail in stats["file_details"]:
            if "error" in detail:
                print(f"  - {detail['filename']}: {detail['error']}")
    
    return stats


if __name__ == "__main__":
    print("=" * 60)
    print("INICIANDO PROCESO DE INGESTA DE DOCUMENTOS")
    print("=" * 60)
    
    try:
        # Ejecutar ingesta
        result = ingest_all_documents()
        
        if result["total_chunks"] > 0:
            print("\n✓ Ingesta completada con éxito!")
        else:
            print("\n⚠ No se procesaron chunks")
    
    except Exception as e:
        print(f"\n✗ Error durante la ingesta: {e}")
        raise

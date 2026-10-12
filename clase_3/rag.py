"""
Sistema RAG: Funciones de procesamiento de documentos, embeddings y búsqueda semántica.

Este módulo contiene:
- Funciones para dividir documentos en chunks
- Generación de embeddings mediante OpenRouter API
- Almacenamiento y recuperación de chunks en PostgreSQL con pgvector
- Búsqueda semántica de información
"""

import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import requests
import psycopg
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Configuración
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
EMBEDDING_MODEL = os.getenv("OPENROUTER_EMBEDDING_MODEL", "openai/text-embedding-3-small")
EMBEDDING_DIMENSIONS = 1536  # Dimensión para text-embedding-3-small

# Configuración PostgreSQL
POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql://postgres:postgres@localhost:5432/rag_db")


def get_embedding(text: str, model: str = EMBEDDING_MODEL, dimensions: int = EMBEDDING_DIMENSIONS) -> List[float]:
    """
    Generar embedding para un texto utilizando OpenRouter API.
    
    Args:
        text: Texto a convertir en embedding
        model: Modelo de embeddings a utilizar
        dimensions: Dimensión del vector (opcional)
    
    Returns:
        Lista de floats representando el embedding
    
    Raises:
        Exception: Si hay error en la llamada a la API
    """
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY no configurada en .env")
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",  # Requerido por OpenRouter
        "X-Title": "RAG System - Embedding Generation",
    }
    
    payload = {
        "model": model,
        "input": text,
    }
    
    if dimensions:
        payload["dimensions"] = dimensions
    
    response = requests.post(
        "https://openrouter.ai/api/v1/embeddings",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    response.raise_for_status()
    
    data = response.json()
    
    # Extraer embedding del primer resultado
    if "data" not in data or len(data["data"]) == 0:
        raise ValueError(f"Respuesta inesperada de la API: {data}")
    
    embedding = data["data"][0]["embedding"]
    
    return embedding


def split_text_into_chunks(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """
    Dividir un texto en chunks con solapamiento.
    
    Args:
        text: Texto a dividir
        chunk_size: Tamaño máximo de cada chunk en caracteres
        overlap: Número de caracteres de solapamiento entre chunks
    
    Returns:
        Lista de chunks (strings)
    """
    if not text or not text.strip():
        return []
    
    # Limpiar texto: reemplazar múltiples espacios y saltos de línea
    text = re.sub(r'\s+', ' ', text).strip()
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        
        # Avanzar considerando el solapamiento
        if end == len(text):
            break
        start = end - overlap
    
    return chunks


def extract_text_from_file(file_path: Path) -> str:
    """
    Extraer texto de un archivo .txt.
    
    Args:
        file_path: Ruta al archivo
    
    Returns:
        Contenido del archivo como string
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def get_connection():
    """
    Obtener conexión a PostgreSQL.
    
    Returns:
        Conexión psycopg
    """
    try:
        conn = psycopg.connect(POSTGRES_URI, connect_timeout=10)
        conn.autocommit = False
        return conn
    except psycopg.Error as e:
        raise ConnectionError(f"Error conectando a PostgreSQL: {e}")


def ensure_tables_exist(conn) -> bool:
    """
    Verificar que las tablas necesarias existen en la base de datos.
    
    Args:
        conn: Conexión a PostgreSQL
    
    Returns:
        True si las tablas existen
    """
    with conn.cursor() as cur:
        # Verificar tabla documents
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'documents'
            )
        """)
        documents_exists = cur.fetchone()[0]
        
        # Verificar tabla document_chunks
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'document_chunks'
            )
        """)
        chunks_exists = cur.fetchone()[0]
        
        return documents_exists and chunks_exists


def store_document(conn, filename: str, filepath: str = None) -> int:
    """
    Almacenar información de un documento en la base de datos.
    
    Args:
        conn: Conexión a PostgreSQL
        filename: Nombre del archivo
        filepath: Ruta del archivo (opcional)
    
    Returns:
        ID del documento creado
    """
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO documents (filename, filepath) VALUES (%s, %s) RETURNING id",
            (filename, filepath)
        )
        document_id = cur.fetchone()[0]
        conn.commit()
        return document_id


def store_chunk(conn, document_id: int, content: str, chunk_index: int, 
                embedding: List[float], metadata: Dict[str, Any] = None) -> int:
    """
    Almacenar un chunk con su embedding en la base de datos.
    
    Args:
        conn: Conexión a PostgreSQL
        document_id: ID del documento padre
        content: Contenido del chunk
        chunk_index: Índice del chunk dentro del documento
        embedding: Vector de embedding
        metadata: Metadatos adicionales (opcional)
    
    Returns:
        ID del chunk creado
    """
    if metadata is None:
        metadata = {}
    
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO document_chunks 
            (document_id, content, chunk_index, embedding, metadata) 
            VALUES (%s, %s, %s, %s, %s) 
            RETURNING id
            """,
            (document_id, content, chunk_index, embedding, metadata)
        )
        chunk_id = cur.fetchone()[0]
        conn.commit()
        return chunk_id


def process_document(file_path: Path, chunk_size: int = 500, overlap: int = 100) -> Dict[str, Any]:
    """
    Procesar un documento completo: leer, dividir en chunks, generar embeddings y almacenar.
    
    Args:
        file_path: Ruta al archivo .txt
        chunk_size: Tamaño de cada chunk
        overlap: Solapamiento entre chunks
    
    Returns:
        Diccionario con estadísticas del procesamiento
    """
    # Leer documento
    text = extract_text_from_file(file_path)
    filename = file_path.name
    
    # Dividir en chunks
    chunks = split_text_into_chunks(text, chunk_size, overlap)
    
    stats = {
        "filename": filename,
        "total_chunks": len(chunks),
        "chunk_size": chunk_size,
        "overlap": overlap,
        "chunks_processed": 0,
        "chunks_stored": 0
    }
    
    if not chunks:
        return stats
    
    # Conectar a PostgreSQL
    conn = get_connection()
    
    try:
        # Verificar que las tablas existen
        if not ensure_tables_exist(conn):
            raise RuntimeError("Las tablas no existen. Ejecuta schema.sql primero.")
        
        # Almacenar documento
        document_id = store_document(conn, filename, str(file_path))
        
        # Procesar cada chunk
        for idx, chunk in enumerate(chunks):
            try:
                # Generar embedding
                embedding = get_embedding(chunk)
                
                # Almacenar chunk con embedding
                metadata = {
                    "filename": filename,
                    "chunk_char_count": len(chunk),
                    "chunk_word_count": len(chunk.split())
                }
                
                store_chunk(conn, document_id, chunk, idx, embedding, metadata)
                
                stats["chunks_processed"] += 1
                stats["chunks_stored"] += 1
                
            except Exception as e:
                print(f"Error procesando chunk {idx} de {filename}: {e}")
                continue
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()
    
    return stats


def semantic_search(query: str, top_k: int = 5, model: str = EMBEDDING_MODEL) -> List[Dict[str, Any]]:
    """
    Realizar búsqueda semántica de una consulta en la base de datos.
    
    Args:
        query: Consulta de búsqueda
        top_k: Número de resultados a devolver
        model: Modelo de embeddings a utilizar
    
    Returns:
        Lista de resultados ordenados por similitud (de mayor a menor)
        Cada resultado contiene: content, filename, similarity, metadata
    """
    # Generar embedding para la consulta
    query_embedding = get_embedding(query, model)
    
    # Conectar a PostgreSQL
    conn = get_connection()
    
    try:
        with conn.cursor() as cur:
            # Consulta pgvector para similitud coseno
            # Ordenar por similitud descendente (1 = más similar, 0 = menos similar)
            cur.execute(
                """
                SELECT 
                    dc.id,
                    dc.content,
                    dc.chunk_index,
                    d.filename,
                    dc.metadata,
                    1 - (dc.embedding <=> %s::vector) as similarity
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                ORDER BY dc.embedding <=> %s::vector
                LIMIT %s
                """,
                (query_embedding, query_embedding, top_k)
            )
            
            results = []
            for row in cur.fetchall():
                chunk_id, content, chunk_index, filename, metadata, similarity = row
                
                result = {
                    "chunk_id": chunk_id,
                    "content": content,
                    "chunk_index": chunk_index,
                    "filename": filename,
                    "similarity": float(similarity),
                    "metadata": metadata or {}
                }
                results.append(result)
            
            return results
    
    except Exception as e:
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    # Prueba de las funciones
    print("Probando funciones de RAG...")
    
    # Test split_text_into_chunks
    test_text = "Este es un texto de prueba. " * 100
    chunks = split_text_into_chunks(test_text, 100, 20)
    print(f"Generados {len(chunks)} chunks")
    
    # Test get_embedding
    try:
        embedding = get_embedding("Hola, esto es una prueba")
        print(f"Embedding generado: {len(embedding)} dimensiones")
    except Exception as e:
        print(f"Error al generar embedding: {e}")
    
    # Test semantic_search (requiere datos en la base de datos)
    try:
        results = semantic_search("¿Qué políticas de seguridad hay?", top_k=3)
        print(f"Resultados de búsqueda: {len(results)}")
        for r in results:
            print(f"  - {r['filename']}: {r['similarity']:.4f}")
    except Exception as e:
        print(f"Error en búsqueda: {e}")

-- Esquema para Sistema RAG con PostgreSQL y pgvector
-- Este archivo crea las tablas necesarias para el sistema de búsqueda semántica

-- Habilitar extensión pgvector (requiere que pgvector esté instalado en PostgreSQL)
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabla de documentos: almacena metadatos de los archivos ingeridos
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(500) NOT NULL,
    filepath TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de chunks: almacena fragmentos de documentos con sus embeddings
-- El campo 'embedding' usa el tipo vector de pgvector con 1536 dimensiones
-- (compatible con text-embedding-3-small de OpenAI)
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para búsqueda eficiente
-- ivfflat es un método de indexación aproximada para vectores (más rápido)
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding 
ON document_chunks 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Índice para consultas por document_id
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id 
ON document_chunks(document_id);

-- Comentarios para documentación
COMMENT ON TABLE documents IS 'Almacena metadatos de los documentos ingeridos en el sistema RAG';
COMMENT ON TABLE document_chunks IS 'Almacena fragmentos (chunks) de documentos con sus representaciones vectoriales (embeddings)';
COMMENT ON COLUMN document_chunks.embedding IS 'Vector de embedding generado por el modelo text-embedding-3-small (1536 dimensiones)';

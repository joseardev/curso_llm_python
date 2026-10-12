"""
Sistema RAG: Aplicación web con FastAPI.

Esta aplicación proporciona:
- API REST para búsqueda semántica
- Interfaz web para consultar documentos
- Integración con el motor RAG (rag.py)
"""

import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from .rag import semantic_search, get_embedding, get_connection

# Cargar variables de entorno
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema RAG - Búsqueda Semántica",
    description="API para búsqueda semántica en documentos usando RAG con OpenRouter y PostgreSQL",
    version="1.0.0"
)

# Configuración CORS
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos (para CSS/JS de la interfaz web)
# app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Página principal con interfaz web para búsqueda.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sistema RAG - Búsqueda Semántica</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 800px;
                margin: 0 auto;
            }
            
            header {
                text-align: center;
                color: white;
                margin-bottom: 30px;
            }
            
            header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            
            header p {
                font-size: 1.1em;
                opacity: 0.9;
            }
            
            .search-box {
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                margin-bottom: 20px;
            }
            
            .search-box h2 {
                color: #333;
                margin-bottom: 15px;
                font-size: 1.5em;
            }
            
            .search-form {
                display: flex;
                gap: 10px;
            }
            
            .search-input {
                flex: 1;
                padding: 15px 20px;
                border: 2px solid #e0e0e0;
                border-radius: 25px;
                font-size: 1em;
                outline: none;
                transition: border-color 0.3s;
            }
            
            .search-input:focus {
                border-color: #667eea;
            }
            
            .search-button {
                padding: 15px 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 1em;
                font-weight: 600;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            .search-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
            }
            
            .search-button:active {
                transform: translateY(0);
            }
            
            .options {
                display: flex;
                gap: 15px;
                margin-top: 15px;
                flex-wrap: wrap;
            }
            
            .option-group {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .option-group label {
                color: #666;
                font-size: 0.9em;
            }
            
            .option-group input, .option-group select {
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 0.9em;
            }
            
            .results-container {
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                min-height: 300px;
            }
            
            .results-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            
            .results-header h2 {
                color: #333;
                font-size: 1.5em;
            }
            
            .result-count {
                color: #667eea;
                font-weight: 600;
            }
            
            .result-item {
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 20px;
                margin-bottom: 15px;
                border-radius: 0 8px 8px 0;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            .result-item:hover {
                transform: translateX(5px);
                box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            }
            
            .result-header {
                display: flex;
                justify-content: space-between;
                align-items: start;
                margin-bottom: 10px;
            }
            
            .result-filename {
                font-weight: 700;
                color: #667eea;
                font-size: 1.1em;
            }
            
            .result-similarity {
                background: #667eea;
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 0.85em;
                font-weight: 600;
            }
            
            .result-content {
                color: #333;
                line-height: 1.6;
                margin-top: 10px;
            }
            
            .result-meta {
                display: flex;
                gap: 15px;
                margin-top: 15px;
                font-size: 0.85em;
                color: #888;
            }
            
            .result-meta span {
                display: flex;
                align-items: center;
                gap: 5px;
            }
            
            .loading {
                text-align: center;
                padding: 40px;
                color: #667eea;
                font-size: 1.2em;
            }
            
            .loading::after {
                content: '...';
                animation: dots 1.5s steps(4, end) infinite;
            }
            
            @keyframes dots {
                0%, 20% { content: '.'; }
                40% { content: '..'; }
                60%, 100% { content: '...'; }
            }
            
            .empty-state {
                text-align: center;
                padding: 40px;
                color: #888;
            }
            
            .empty-state h3 {
                margin-bottom: 10px;
                color: #666;
            }
            
            .error-message {
                background: #fee;
                color: #c33;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 15px;
                border-left: 4px solid #c33;
            }
            
            footer {
                text-align: center;
                color: white;
                margin-top: 30px;
                opacity: 0.7;
                font-size: 0.9em;
            }
            
            .stats {
                display: flex;
                gap: 20px;
                margin-top: 15px;
                font-size: 0.9em;
            }
            
            .stat-item {
                display: flex;
                align-items: center;
                gap: 8px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🔍 Sistema RAG</h1>
                <p>Búsqueda Semántica de Documentos</p>
            </header>
            
            <div class="search-box">
                <h2>Consultar Documentos</h2>
                <form class="search-form" id="searchForm">
                    <input 
                        type="text" 
                        class="search-input" 
                        id="query" 
                        placeholder="Ej: ¿Qué políticas de seguridad hay?" 
                        required
                        autofocus
                    >
                    <button type="submit" class="search-button">
                        Buscar
                    </button>
                </form>
                
                <div class="options">
                    <div class="option-group">
                        <label for="topK">Resultados:</label>
                        <select id="topK" name="topK">
                            <option value="3">3</option>
                            <option value="5" selected>5</option>
                            <option value="10">10</option>
                            <option value="20">20</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="results-container" id="resultsContainer">
                <div class="empty-state">
                    <h3>Introduce una consulta para buscar</h3>
                    <p>El sistema buscará en los documentos ingeridos y mostrará los resultados más relevantes.</p>
                </div>
            </div>
            
            <footer>
                <p>Sistema RAG con OpenRouter, PostgreSQL y pgvector</p>
            </footer>
        </div>
        
        <script>
            const searchForm = document.getElementById('searchForm');
            const resultsContainer = document.getElementById('resultsContainer');
            
            searchForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const query = document.getElementById('query').value.trim();
                const topK = document.getElementById('topK').value;
                
                if (!query) return;
                
                // Mostrar estado de carga
                resultsContainer.innerHTML = '<div class="loading">Buscando</div>';
                
                try {
                    const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&top_k=${topK}`);
                    const data = await response.json();
                    
                    if (data.error) {
                        resultsContainer.innerHTML = `<div class="error-message">${data.error}</div>`;
                        return;
                    }
                    
                    renderResults(data.results, query);
                    
                } catch (error) {
                    resultsContainer.innerHTML = '<div class="error-message">Error al realizar la búsqueda</div>';
                    console.error('Error:', error);
                }
            });
            
            function renderResults(results, query) {
                if (!results || results.length === 0) {
                    resultsContainer.innerHTML = `
                        <div class="empty-state">
                            <h3>No se encontraron resultados</h3>
                            <p>No hay documentos que coincidan con "${query}"</p>
                        </div>
                    `;
                    return;
                }
                
                let html = `
                    <div class="results-header">
                        <h2>Resultados</h2>
                        <span class="result-count">${results.length} encontrados</span>
                    </div>
                `;
                
                results.forEach(result => {
                    const similarityPercent = (result.similarity * 100).toFixed(1);
                    const filename = result.filename || 'Desconocido';
                    const content = result.content.substring(0, 500);
                    const chunkIndex = result.chunk_index !== undefined ? result.chunk_index + 1 : 'N/A';
                    const wordCount = result.metadata?.chunk_word_count || 'N/A';
                    
                    html += `
                        <div class="result-item">
                            <div class="result-header">
                                <div class="result-filename">📄 ${filename}</div>
                                <div class="result-similarity">${similarityPercent}% similar</div>
                            </div>
                            <div class="result-content">${escapeHtml(content)}...</div>
                            <div class="result-meta">
                                <span>🔢 Chunk: ${chunkIndex}</span>
                                <span>📝 Palabras: ${wordCount}</span>
                                <span>🎯 ID: ${result.chunk_id}</span>
                            </div>
                        </div>
                    `;
                });
                
                resultsContainer.innerHTML = html;
            }
            
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            // Enviar búsqueda con Enter en el campo de texto
            document.getElementById('query').addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    searchForm.dispatchEvent(new Event('submit'));
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/api/search")
async def search_documents(
    q: str,
    top_k: int = 5
):
    """
    Endpoint de búsqueda semántica.
    
    Parámetros:
    - q: Consulta de búsqueda (query)
    - top_k: Número máximo de resultados a devolver (por defecto: 5)
    
    Returns:
        JSON con los resultados de la búsqueda
    """
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="La consulta no puede estar vacía")
    
    try:
        # Realizar búsqueda semántica
        results = semantic_search(q, top_k=top_k)
        
        # Formatear resultados para la API
        formatted_results = []
        for r in results:
            formatted_results.append({
                "chunk_id": r["chunk_id"],
                "content": r["content"],
                "chunk_index": r["chunk_index"],
                "filename": r["filename"],
                "similarity": r["similarity"],
                "metadata": r["metadata"]
            })
        
        return {
            "success": True,
            "query": q,
            "results": formatted_results,
            "count": len(formatted_results)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al realizar la búsqueda: {str(e)}"
        )


@app.get("/api/health")
async def health_check():
    """
    Endpoint de verificación de salud del servicio.
    """
    try:
        # Verificar conexión a PostgreSQL
        conn = get_connection()
        
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM document_chunks")
            chunk_count = cur.fetchone()[0]
        
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "chunks_in_database": chunk_count,
            "openrouter_api_key": bool(os.getenv("OPENROUTER_API_KEY"))
        }
    except Exception as e:
        return {
            "status": "degraded",
            "database": "disconnected",
            "error": str(e)
        }


@app.get("/api/stats")
async def get_stats():
    """
    Endpoint para obtener estadísticas del sistema.
    """
    try:
        conn = get_connection()
        
        with conn.cursor() as cur:
            # Contar documentos
            cur.execute("SELECT COUNT(*) FROM documents")
            doc_count = cur.fetchone()[0]
            
            # Contar chunks
            cur.execute("SELECT COUNT(*) FROM document_chunks")
            chunk_count = cur.fetchone()[0]
            
            # Tamaño promedio de chunks
            cur.execute("SELECT AVG(LENGTH(content)) FROM document_chunks")
            avg_chunk_size = cur.fetchone()[0] or 0
            
            # Documentos más recientes
            cur.execute("""
                SELECT filename FROM documents 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            recent_docs = [row[0] for row in cur.fetchall()]
        
        conn.close()
        
        return {
            "documents_count": doc_count,
            "chunks_count": chunk_count,
            "average_chunk_size": float(avg_chunk_size),
            "recent_documents": recent_docs
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("INICIANDO SERVIDOR FASTAPI - SISTEMA RAG")
    print("=" * 60)
    print("Accede a la aplicación en: http://localhost:8000")
    print("API de búsqueda: http://localhost:8000/api/search?q=término")
    print(" " * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )

# Clase 3: Sistema RAG

Esta carpeta reúne el motor RAG, la ingesta, el esquema SQL, los documentos y
la aplicación FastAPI de la clase.

## Estructura

```text
clase_3/
├── documents/      # Documentos .txt de ejemplo
├── embeddings.py   # Prueba del endpoint de embeddings
├── ingest.py       # Ingesta de documentos en PostgreSQL
├── main.py         # API e interfaz web FastAPI
├── rag.py          # Chunks, embeddings y búsqueda semántica
└── schema.sql      # Esquema PostgreSQL/pgvector
```

La configuración `.env`, el entorno virtual `.venv` y `requirements.txt` se
comparten desde la carpeta `a1-chat-llm`.

## Ejecutar

Desde `a1-chat-llm`, instala las dependencias si hace falta y ejecuta la
ingesta o el servidor con el entorno virtual de esa carpeta:

```powershell
.venv\Scripts\python.exe -m clase_3.ingest
.venv\Scripts\python.exe -m uvicorn clase_3.main:app --reload
```

La app está disponible en `http://127.0.0.1:8000`. Crea primero las tablas
ejecutando `clase_3/schema.sql` en la base de datos configurada en `.env`.

# Plan de Trabajo: Sistema RAG

## Parte 1: Preparar el Entorno
- [x] 1.1 Crear y activar entorno virtual (`python -m venv .venv`).
- [x] 1.2 Instalar dependencias (`pip install -r requirements.txt`).
- [x] 1.3 Configurar variables de entorno (`.env`).
- [ ] 1.4 Preparar base de datos PostgreSQL y ejecutar `schema.sql`.

## Parte 2: Construir el Motor de Ingesta (`ingest.py` y `rag.py`)
- [ ] 2.1 Implementar lectura de archivos `.txt` en `documents/`.
- [ ] 2.2 Implementar función de división en fragmentos (chunks) en `rag.py`.
- [ ] 2.3 Implementar generación de embeddings (OpenRouter API) en `rag.py`.
- [ ] 2.4 Implementar almacenamiento de chunks y vectores en PostgreSQL.

## Parte 3: Construir la Búsqueda Semántica (`rag.py`)
- [ ] 3.1 Implementar generación de embedding para una consulta de usuario.
- [ ] 3.2 Implementar búsqueda de similitud en pgvector.
- [ ] 3.3 Validar calidad de los resultados obtenidos.

## Parte 4: Integración Web (`main.py`)
- [ ] 4.1 Revisar estructura de `main.py` (FastAPI).
- [ ] 4.2 Conectar ruta de búsqueda en `main.py` con `rag.py`.
- [ ] 4.3 Pruebas de integración en navegador.

## Parte 5: Construir el RAG Completo
- [ ] 5.1 Integrar LLM con el contexto recuperado (proceso RAG final).
- [ ] 5.2 Comparar resultados de búsqueda vs. generación.
- [ ] 5.3 Pruebas de resistencia (preguntas fuera de contexto/alucinaciones).

## Ampliaciones (Opcional)
- [ ] A1: Investigar e implementar con LlamaIndex.
- [ ] A2: Mejorar ingesta (progreso, otros formatos de archivo, metadatos).

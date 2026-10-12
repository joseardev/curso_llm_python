# Clase 2

Aquí están los ejemplos de herramientas con memoria:

- `tools_memoria_corto_plazo.py`: memoria en el proceso (InMemorySaver).
- `tools_memoria_postgres.py`: memoria persistente en PostgreSQL.

Desde `a1-chat-llm`, ejecuta:

```powershell
.venv\Scripts\python.exe -m clase_2.tools_memoria_corto_plazo
.venv\Scripts\python.exe -m clase_2.tools_memoria_postgres --thread-id conversacion-1
```

El `.env`, el entorno `.venv` y `requirements.txt` se comparten desde
`a1-chat-llm`. Para PostgreSQL, configura `POSTGRES_URI` en ese `.env`.

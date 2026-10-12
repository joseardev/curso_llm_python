"""Ejemplo de agente con herramientas y memoria persistente en PostgreSQL.

Instalación: python -m pip install -r requirements.txt
Configura POSTGRES_URI en el .env de a1-chat-llm.
Ejecución desde a1-chat-llm: python -m clase_2.tools_memoria_postgres --thread-id conversacion-1
Repite el mismo comando para retomar la conversación después de cerrar el script.
"""

import argparse
import os
import random
from pathlib import Path

from dotenv import load_dotenv
from langchain.messages import HumanMessage
from langchain.tools import tool


# Las mismas herramientas del ejemplo con InMemorySaver.
@tool(parse_docstring=True)
def get_weather(city: str, date: str) -> str:
    """Función que devuelve el clima de la ciudad indicada como parámetro.

    Args:
        city (str): Nombre de la ciudad.
        date (str): Fecha para la cual se desea conocer el clima, en formato 'YYYY-MM-DD'.

    Returns:
        str: Clima de la ciudad.
    """
    # Simulamos la obtención del clima.
    opciones_clima = ["soleado", "lluvioso", "nublado", "tormentoso", "nevado"]
    clima = opciones_clima[hash(city + date) % len(opciones_clima)]
    temperatura = random.randint(-5, 35)
    return f"El clima en {city} el {date} es {clima} con una temperatura de {temperatura}°C."


@tool(parse_docstring=True)
def get_current_date() -> str:
    """Función que devuelve la fecha actual en formato 'YYYY-MM-DD'.

    Returns:
        str: Fecha actual.
    """
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d")


SYSTEM_PROMPT = (
    "Eres un asistente de IA que ayuda a los usuarios a obtener información "
    "sobre el clima y la fecha actual. Responde en español."
)


def crear_agente(checkpointer):
    from langchain.agents import create_agent
    from langchain.chat_models import init_chat_model

    llm = init_chat_model(
        os.getenv("OPENROUTER_MODEL", "openai/gpt-6-luna"),
        model_provider="openrouter",
    )
    return create_agent(
        model=llm,
        tools=[get_weather, get_current_date],
        checkpointer=checkpointer,
        system_prompt=SYSTEM_PROMPT,
    )


def ejecutar_chat(agente, thread_id: str):
    # El mismo ID recupera la misma conversación, incluso después de reiniciar.
    config = {"configurable": {"thread_id": thread_id}}
    print(f"Conversación: {thread_id}")
    print("Escribe 'exit' o 'quit' para salir. El historial queda en PostgreSQL.")

    while True:
        try:
            pregunta = input("Pregunta: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if pregunta.lower() in ["exit", "quit"]:
            break
        if not pregunta:
            continue

        # Enviamos solo el nuevo mensaje; PostgresSaver recupera los anteriores.
        # El historial sigue aumentando el contexto del modelo: no se resume solo.
        respuesta = agente.invoke(
            {"messages": [HumanMessage(content=pregunta)]},
            config=config,
        )
        print(f"Respuesta: {respuesta['messages'][-1].text}")

        for tool_result in respuesta.get("tool_results", []):
            print(f"Resultado de la herramienta '{tool_result['tool_name']}': {tool_result['output']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--thread-id",
        default="clima-demo",
        help="ID de la conversación (por defecto: clima-demo). Usa otro para empezar una nueva.",
    )
    args = parser.parse_args()
    if not args.thread_id.strip() or len(args.thread_id) > 255:
        parser.error("--thread-id debe tener entre 1 y 255 caracteres y no estar vacío.")

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    postgres_uri = os.getenv("POSTGRES_URI", "").strip()
    if not postgres_uri:
        parser.error(
            "Configura POSTGRES_URI en .env, por ejemplo: "
            "postgresql://usuario:password@localhost:5432/chat_memoria"
        )

    from langgraph.checkpoint.postgres import PostgresSaver
    import psycopg
    from psycopg.conninfo import conninfo_to_dict, make_conninfo

    fase = "conectar con PostgreSQL"
    connection_parameters = {}
    try:
        connection_parameters = conninfo_to_dict(postgres_uri)
        # El límite se aplica a cada servidor/dirección de la conexión.
        # make_conninfo funciona tanto con URI como con parámetros key=value.
        conninfo = make_conninfo(postgres_uri, connect_timeout=5)
        print("Conectando a PostgreSQL (límite de 5 segundos por destino)...", flush=True)

        # El 'with' mantiene abierta la conexión durante TODA la conversación.
        # Al salir, se cierra la conexión; los datos siguen guardados en PostgreSQL.
        with PostgresSaver.from_conn_string(conninfo) as checkpointer:
            fase = "preparar las tablas de memoria"
            print("Conexión establecida. Preparando las tablas de memoria...", flush=True)
            # No crea la base de datos; esta debe existir antes de ejecutar el script.
            checkpointer.setup()
            print("Memoria preparada. Creando el agente...", flush=True)
            agente = crear_agente(checkpointer)
            fase = "leer o guardar la conversación"
            ejecutar_chat(agente, args.thread_id)
    except psycopg.Error as exc:
        # Mostramos el diagnóstico sin exponer la cadena de conexión ni su contraseña.
        mensaje = str(exc)
        for secreto in (postgres_uri, connection_parameters.get("password", "")):
            if secreto:
                mensaje = mensaje.replace(secreto, "[oculto]")
        raise SystemExit(
            f"Error de PostgreSQL al {fase}:\n{mensaje}\n"
            "Comprueba que el servidor esté arrancado y revisa el host, puerto, "
            "credenciales y base de datos de POSTGRES_URI."
        ) from None


if __name__ == "__main__":
    main()

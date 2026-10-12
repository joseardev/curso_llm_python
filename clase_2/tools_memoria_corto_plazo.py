import random
import uuid
from pathlib import Path

from dotenv import load_dotenv
from langchain.messages import HumanMessage
from langchain.tools import tool


# Definición de herramientas para el agente.
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

def crear_agente():
    from langchain.chat_models import init_chat_model
    from langchain.agents import create_agent
    from langgraph.checkpoint.memory import InMemorySaver
    import os

    # Carga de .env: leemos las credenciales y el modelo desde la carpeta del fichero.
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

    llm = init_chat_model(
        os.getenv("OPENROUTER_MODEL", "openai/gpt-6-luna"),
        model_provider="openrouter",
    )
    return create_agent(
        model=llm,
        tools=[get_weather, get_current_date],
        checkpointer=InMemorySaver(),
        system_prompt=SYSTEM_PROMPT,
    )


if __name__ == "__main__":
    agente = crear_agente()
    # Historial: thread_id identifica la conversación y se mantiene en todos los turnos.
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

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

        mensaje_pregunta = HumanMessage(content=pregunta)
        # invoke recibe un diccionario con "messages" y el thread_id dentro de config.
        # Enviamos solo el nuevo mensaje; InMemorySaver recupera los anteriores.
        respuesta = agente.invoke(
            {"messages": [mensaje_pregunta]},
            config=config,
        )

        # respuesta["messages"] contiene el historial; [-1].text es la respuesta final.
        print(f"Respuesta: {respuesta['messages'][-1].text}")

        for tool_result in respuesta.get("tool_results", []):
            print(f"Resultado de la herramienta '{tool_result['tool_name']}': {tool_result['output']}")

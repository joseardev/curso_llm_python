import os
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage
from langchain.tools import tool

SYSTEM_PROMPT = (
    "Eres un asistente de IA que ayuda a los usuarios a encontrar información "
    "y responder preguntas. Responde en español. "
    "Usa la herramienta fecha_actual cuando necesites saber la fecha de hoy."
)


@tool
def fecha_actual() -> str:
    """Devuelve la fecha actual del equipo en formato YYYY-MM-DD."""
    return date.today().isoformat()


def leer_agenda(desde: datetime, hasta: datetime) -> list[tuple[datetime, str]]:
    """Devuelve una lista de eventos en la agenda entre las fechas dadas."""
    # Aquí iría la lógica para leer la agenda real.
    # Por ahora, devolvemos un ejemplo estático.
    return [
        f"Evento 1: {desde} - {hasta}",
        f"Evento 2: {desde} - {hasta}",
    ]

def crear_agente():
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    if not os.getenv("OPENROUTER_API_KEY"):
        raise ValueError("Configura OPENROUTER_API_KEY en el fichero .env.")

    llm = init_chat_model(
        os.getenv("OPENROUTER_MODEL", "openai/gpt-6-luna"),
        model_provider="openrouter",
    )
    return create_agent(
        model=llm,
        tools=[fecha_actual],
        system_prompt=SYSTEM_PROMPT,
    )


def main() -> None:
    agente = crear_agente()
    mensajes = []
    print("Asistente IA. Escribe 'exit' o 'quit' para salir.")

    while True:
        try:
            pregunta = input("Pregunta: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if pregunta.lower() in {"exit", "quit"}:
            break
        if not pregunta:
            continue

        respuesta = agente.invoke(
            {"messages": [*mensajes, HumanMessage(content=pregunta)]}
        )
        mensajes = respuesta["messages"]
        print(f"Agente: {mensajes[-1].text}")


if __name__ == "__main__":
    main()

from dataclasses import dataclass
import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

@dataclass
class Message:
    role: str
    content: str


def chat(messages: list[Message]) -> str:
    """Envía los mensajes al modelo y devuelve su respuesta."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("La variable de entorno OPENROUTER_API_KEY no está configurada.")

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": os.getenv(
                "OPENROUTER_MODEL", "openai/gpt-6-luna"
            ),
            "messages": [
                {"role": message.role, "content": message.content}
                for message in messages
            ],
        }),
        timeout=60,
    )
    if not response.ok:
        try:
            error_message = response.json()["error"]["message"]
        except (ValueError, KeyError, TypeError):
            error_message = response.text or response.reason
        raise requests.HTTPError(
            f"OpenRouter ({response.status_code}): {error_message}",
            response=response,
        )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def main():
    messages = []

    print("Asistente IA. Escribe 'exit' para salir.")

    while True:
        user_input = input("Tú: ")

        if user_input.lower() == "exit":
            break

        messages.append(Message(role="user", content=user_input))

        # llamar al LLM
        try:
            assistant_response = chat(messages)
        except (requests.RequestException, ValueError) as error:
            messages.pop()
            print(f"Error: {error}")
            continue

        #  mostrar respuesta
        print(f"IA: {assistant_response}")
        
        # añadir respuesta al historial
        messages.append(Message(role="assistant", content=assistant_response))


if __name__ == "__main__":
    main()

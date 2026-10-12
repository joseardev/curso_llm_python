import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage, HumanMessage, SystemMessage

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


SYSTEM_PROMPT = """eres un traductor y todo lo que recibas lo traducirás al frances. 
"""
model = init_chat_model(
    os.getenv("OPENROUTER_MODEL", "openai/gpt-6-luna"),
    model_provider="openrouter",
)

conversation = [
    SystemMessage(content=SYSTEM_PROMPT)
]

while True:
    pregunta = input("User: ")
    if pregunta.lower() == "exit":
        break

    conversation.append(HumanMessage(content=pregunta))
    response = model.invoke(conversation)
    assistant_response = response.content
    print(f"Assistant: {assistant_response}")
    conversation.append(AIMessage(content=assistant_response))

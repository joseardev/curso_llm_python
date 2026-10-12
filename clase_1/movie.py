import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

class Movie(BaseModel):
    title: str = Field(..., description="Título de la película")
    director: str = Field(..., description="Director de la película")
    year: int = Field(..., description="Año de estreno de la película")
    genre: str = Field(..., description="Género de la película")
    rating: float = Field(..., description="Calificación de la película")


class Movies(BaseModel):
    movies: list[Movie] = Field(
        ..., min_length=5, max_length=5, description="Información sobre cinco películas"
    )


model = init_chat_model(
    os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3-super-120b-a12b:free"),
    model_provider="openrouter",
)

structured_model = model.with_structured_output(Movies, method="json_schema")
response = structured_model.invoke(
    [
        SystemMessage(content="Eres un experto en cine."),
        HumanMessage(content="Dame información sobre 5 películas."),
    ]
)
print(response.model_dump_json(indent=2))

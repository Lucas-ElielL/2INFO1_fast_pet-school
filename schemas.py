from pydantic import BaseModel, ConfigDict, Field


class petEntrada(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    nome: str = Field(min_length=1, max_length=100)
    especie: str = Field(min_length=1, max_length=50)
    tutor_id: int = Field(ge=0)

class tutorEntrada(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    nome: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=1, max_length=100)
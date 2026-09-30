from typing import Optional
from pydantic import BaseModel, Field


class RecargaIn(BaseModel):
    telefone: str = Field(pattern=r"^\d{10,11}$", examples=["11999999999"])
    valor: float = Field(gt=0, examples=[20.0])


class ContaIn(BaseModel):
    linha_digitavel: str = Field(min_length=44, max_length=60)
    descricao: Optional[str] = None
    data_agendamento: Optional[str] = Field(default=None, examples=["2026-10-05"])
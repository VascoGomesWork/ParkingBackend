from pydantic import BaseModel, Field
from typing import Optional

class Item(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    description: Optional[str] = None

class Carro(BaseModel):
    matricula: str
    marca: str
    modelo: str
    ano: int
    combustivel: str

class Lugar(BaseModel):
    id: int
    estado: str
    tipo: bool
    coordenadas: list
    carro: Carro

class Park(BaseModel):
    nome: str
    num_lugares: int
    lugar: Lugar

#class Cidade(BaseModel):
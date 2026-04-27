from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class Servidora:
    nome: str
    data_nascimento: date
    data_ingresso: date


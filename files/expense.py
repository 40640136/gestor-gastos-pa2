"""
models/expense.py
Modelo de datos que representa un gasto individual.
"""

from dataclasses import dataclass, field
from datetime import datetime


CATEGORIAS_VALIDAS = {
    "alimentacion",
    "transporte",
    "salud",
    "entretenimiento",
    "educacion",
    "hogar",
    "otros",
}


@dataclass
class Gasto:
    """Representa un gasto con todos sus atributos relevantes."""

    descripcion: str
    monto: float
    categoria: str
    fecha: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    gasto_id: int = field(default=0)

    def to_dict(self) -> dict:
        """Convierte el gasto a un diccionario para persistencia JSON."""
        return {
            "gasto_id": self.gasto_id,
            "descripcion": self.descripcion,
            "monto": self.monto,
            "categoria": self.categoria,
            "fecha": self.fecha,
        }

    @staticmethod
    def from_dict(data: dict) -> "Gasto":
        """Crea un objeto Gasto a partir de un diccionario JSON."""
        return Gasto(
            gasto_id=data["gasto_id"],
            descripcion=data["descripcion"],
            monto=data["monto"],
            categoria=data["categoria"],
            fecha=data["fecha"],
        )

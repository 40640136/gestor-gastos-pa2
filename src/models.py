"""
models.py
Modelo ORM para la entidad Gasto usando SQLAlchemy declarative base.
Define la tabla 'gastos' y las validaciones a nivel de columna.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, CheckConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()

CATEGORIAS_VALIDAS = frozenset({
    "alimentacion",
    "transporte",
    "salud",
    "entretenimiento",
    "educacion",
    "hogar",
    "otros",
})


class Gasto(Base):
    """
    Entidad persistida que representa un gasto personal.

    Columnas:
        id          -- Clave primaria autoincremental.
        descripcion -- Texto descriptivo del gasto (no vacío).
        monto       -- Valor monetario en soles (estrictamente positivo).
        categoria   -- Categoría semántica; debe pertenecer a CATEGORIAS_VALIDAS.
        fecha       -- Fecha del gasto en formato ISO (YYYY-MM-DD).
    """

    __tablename__ = "gastos"
    __table_args__ = (
        CheckConstraint("monto > 0", name="ck_monto_positivo"),
        CheckConstraint("length(trim(descripcion)) > 0", name="ck_descripcion_no_vacia"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String(255), nullable=False)
    monto = Column(Float, nullable=False)
    categoria = Column(String(50), nullable=False)
    fecha = Column(String(10), nullable=False)

    def __init__(self, descripcion, monto, categoria, fecha=None, **kwargs):
        super().__init__(**kwargs)
        self.descripcion = descripcion
        self.monto = monto
        self.categoria = categoria
        self.fecha = fecha or datetime.now().strftime("%Y-%m-%d")

    def to_dict(self) -> dict:
        """Serializa el gasto a diccionario (útil para tests y presentación)."""
        return {
            "id": self.id,
            "descripcion": self.descripcion,
            "monto": self.monto,
            "categoria": self.categoria,
            "fecha": self.fecha,
        }

    def __repr__(self) -> str:
        return f"<Gasto id={self.id} descripcion='{self.descripcion}' monto={self.monto}>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Gasto):
            return False
        return self.id == other.id

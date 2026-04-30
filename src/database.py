"""
database.py
Configuración del motor SQLAlchemy y fábrica de sesiones.
Centraliza la creación de la base de datos para facilitar la inyección
de distintos motores en tests (SQLite en memoria) y en producción (SQLite en archivo).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.models import Base

DEFAULT_DB_URL = "sqlite:///gastos.db"


def crear_engine(url: str = DEFAULT_DB_URL):
    """Crea y devuelve un engine SQLAlchemy configurado."""
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(url, connect_args=connect_args, echo=False)


def inicializar_base_de_datos(engine) -> None:
    """Crea todas las tablas definidas en los modelos si no existen."""
    Base.metadata.create_all(bind=engine)


def crear_sesion(engine) -> Session:
    """Devuelve una nueva sesión ligada al engine proporcionado."""
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return SessionLocal()

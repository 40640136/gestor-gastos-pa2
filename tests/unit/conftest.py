"""
conftest.py
Fixtures compartidas entre todos los módulos de test.
Usa SQLite en memoria para garantizar aislamiento y velocidad.
Cada test recibe una sesión y repositorio limpios (sin estado compartido).
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base
from src.repository import RepositorioGastos
from src.service import ServicioGastos


@pytest.fixture(scope="function")
def engine():
    """Engine SQLite en memoria — se recrea por cada función de test."""
    _engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=_engine)
    yield _engine
    Base.metadata.drop_all(bind=_engine)
    _engine.dispose()


@pytest.fixture(scope="function")
def sesion(engine):
    """Sesión ligada al engine en memoria — se cierra tras cada test."""
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    _sesion = SessionLocal()
    yield _sesion
    _sesion.close()


@pytest.fixture(scope="function")
def repositorio(sesion):
    """Repositorio listo para usar en tests unitarios."""
    return RepositorioGastos(sesion)


@pytest.fixture(scope="function")
def servicio(repositorio):
    """Servicio listo para usar en tests unitarios e integración."""
    return ServicioGastos(repositorio)


@pytest.fixture
def gasto_valido_data():
    """Datos válidos de un gasto — reutilizables en múltiples tests."""
    return {
        "descripcion": "Almuerzo en restaurante",
        "monto": 35.50,
        "categoria": "alimentacion",
    }

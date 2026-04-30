"""
repository.py
Capa de acceso a datos implementada con SQLAlchemy ORM.
Aplica el patrón Repository: aísla la persistencia de la lógica de negocio.
El servicio solo conoce esta interfaz, nunca la sesión directamente.
"""

from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.models import Gasto
from src.exceptions import GastoNoEncontradoError, DatabaseError


class RepositorioGastos:
    """Operaciones CRUD sobre la tabla 'gastos' usando SQLAlchemy ORM."""

    def __init__(self, sesion: Session):
        self._sesion = sesion

    # ── Escritura ──────────────────────────────────────────────────────

    def guardar(self, gasto: Gasto) -> Gasto:
        """Persiste un nuevo gasto y retorna la instancia con su ID asignado."""
        try:
            self._sesion.add(gasto)
            self._sesion.commit()
            self._sesion.refresh(gasto)
            return gasto
        except SQLAlchemyError as error:
            self._sesion.rollback()
            raise DatabaseError("guardar", str(error)) from error

    def eliminar(self, gasto_id: int) -> Gasto:
        """Elimina el gasto con el ID indicado y retorna la instancia eliminada."""
        gasto = self.buscar_por_id(gasto_id)
        try:
            self._sesion.delete(gasto)
            self._sesion.commit()
            return gasto
        except SQLAlchemyError as error:
            self._sesion.rollback()
            raise DatabaseError("eliminar", str(error)) from error

    # ── Lectura ────────────────────────────────────────────────────────

    def buscar_por_id(self, gasto_id: int) -> Gasto:
        """Retorna el gasto con el ID dado o lanza GastoNoEncontradoError."""
        gasto = self._sesion.get(Gasto, gasto_id)
        if gasto is None:
            raise GastoNoEncontradoError(gasto_id)
        return gasto

    def listar_todos(self) -> List[Gasto]:
        """Retorna todos los gastos ordenados por fecha descendente."""
        return (
            self._sesion.query(Gasto)
            .order_by(Gasto.fecha.desc(), Gasto.id.desc())
            .all()
        )

    def listar_por_categoria(self, categoria: str) -> List[Gasto]:
        """Retorna los gastos filtrados por categoría."""
        return (
            self._sesion.query(Gasto)
            .filter(Gasto.categoria == categoria.lower())
            .order_by(Gasto.fecha.desc())
            .all()
        )

    def suma_por_categoria(self) -> dict:
        """Retorna un diccionario {categoria: total} con la suma por categoría."""
        from sqlalchemy import func
        resultados = (
            self._sesion.query(Gasto.categoria, func.sum(Gasto.monto))
            .group_by(Gasto.categoria)
            .all()
        )
        return {cat: round(total, 2) for cat, total in resultados}

    def total_general(self) -> float:
        """Retorna la suma de todos los montos registrados."""
        from sqlalchemy import func
        resultado = self._sesion.query(func.sum(Gasto.monto)).scalar()
        return round(resultado or 0.0, 2)

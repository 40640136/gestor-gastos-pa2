"""
services/expense_service.py
Capa de lógica de negocio para la gestión de gastos.
Valida las entradas y coordina operaciones entre el modelo y el repositorio.
"""

from typing import List, Optional, Dict

from models.expense import Gasto, CATEGORIAS_VALIDAS
from storage.json_repository import RepositorioGastos
from exceptions import (
    MontoInvalidoError,
    CategoriaInvalidaError,
    DescripcionVaciaError,
    GastoNoEncontradoError,
)


class ServicioGastos:
    """Orquesta las operaciones CRUD y estadísticas sobre los gastos."""

    def __init__(self, repositorio: Optional[RepositorioGastos] = None):
        self._repo = repositorio or RepositorioGastos()
        self._gastos: List[Gasto] = self._repo.cargar_todos()
        self._siguiente_id: int = self._calcular_siguiente_id()

    # ------------------------------------------------------------------ #
    #  Operaciones CRUD                                                    #
    # ------------------------------------------------------------------ #

    def agregar_gasto(self, descripcion: str, monto: float, categoria: str) -> Gasto:
        """Valida y registra un nuevo gasto."""
        self._validar_descripcion(descripcion)
        self._validar_monto(monto)
        self._validar_categoria(categoria)

        nuevo = Gasto(
            descripcion=descripcion.strip(),
            monto=round(monto, 2),
            categoria=categoria.lower(),
            gasto_id=self._siguiente_id,
        )
        self._gastos.append(nuevo)
        self._siguiente_id += 1
        self._repo.guardar_todos(self._gastos)
        return nuevo

    def listar_gastos(self, categoria: Optional[str] = None) -> List[Gasto]:
        """Retorna todos los gastos, opcionalmente filtrados por categoría."""
        if categoria is None:
            return list(self._gastos)
        categoria = categoria.lower()
        self._validar_categoria(categoria)
        return [g for g in self._gastos if g.categoria == categoria]

    def eliminar_gasto(self, gasto_id: int) -> Gasto:
        """Elimina un gasto por ID y retorna el gasto eliminado."""
        gasto = self._buscar_por_id(gasto_id)
        self._gastos.remove(gasto)
        self._repo.guardar_todos(self._gastos)
        return gasto

    def resumen_por_categoria(self) -> Dict[str, float]:
        """Calcula el total gastado agrupado por categoría."""
        resumen: Dict[str, float] = {}
        for gasto in self._gastos:
            resumen[gasto.categoria] = round(
                resumen.get(gasto.categoria, 0.0) + gasto.monto, 2
            )
        return dict(sorted(resumen.items(), key=lambda x: x[1], reverse=True))

    def total_general(self) -> float:
        """Calcula el monto total de todos los gastos registrados."""
        return round(sum(g.monto for g in self._gastos), 2)

    # ------------------------------------------------------------------ #
    #  Métodos privados de validación y utilidad                          #
    # ------------------------------------------------------------------ #

    def _calcular_siguiente_id(self) -> int:
        if not self._gastos:
            return 1
        return max(g.gasto_id for g in self._gastos) + 1

    def _buscar_por_id(self, gasto_id: int) -> Gasto:
        for gasto in self._gastos:
            if gasto.gasto_id == gasto_id:
                return gasto
        raise GastoNoEncontradoError(gasto_id)

    @staticmethod
    def _validar_descripcion(descripcion: str) -> None:
        if not descripcion or not descripcion.strip():
            raise DescripcionVaciaError()

    @staticmethod
    def _validar_monto(monto: float) -> None:
        if monto <= 0:
            raise MontoInvalidoError(monto)

    @staticmethod
    def _validar_categoria(categoria: str) -> None:
        if categoria.lower() not in CATEGORIAS_VALIDAS:
            raise CategoriaInvalidaError(categoria, CATEGORIAS_VALIDAS)

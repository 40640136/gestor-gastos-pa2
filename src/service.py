"""
service.py
Capa de lógica de negocio para el gestor de gastos.
Valida entradas, aplica reglas de dominio y delega la persistencia al repositorio.
Sigue el principio de responsabilidad única (SRP): solo conoce las reglas de negocio.
"""

from typing import List, Optional, Dict

from src.models import Gasto, CATEGORIAS_VALIDAS
from src.repository import RepositorioGastos
from src.exceptions import (
    MontoInvalidoError,
    CategoriaInvalidaError,
    DescripcionVaciaError,
)


class ServicioGastos:
    """Orquesta las operaciones sobre gastos aplicando validaciones de dominio."""

    def __init__(self, repositorio: RepositorioGastos):
        self._repo = repositorio

    # ── Operaciones principales ────────────────────────────────────────

    def agregar_gasto(
        self, descripcion: str, monto: float, categoria: str, fecha: Optional[str] = None
    ) -> Gasto:
        """Valida los datos y registra un nuevo gasto en la base de datos."""
        self._validar_descripcion(descripcion)
        self._validar_monto(monto)
        self._validar_categoria(categoria)

        gasto = Gasto(
            descripcion=descripcion.strip(),
            monto=round(monto, 2),
            categoria=categoria.lower(),
        )
        if fecha:
            gasto.fecha = fecha

        return self._repo.guardar(gasto)

    def eliminar_gasto(self, gasto_id: int) -> Gasto:
        """Elimina un gasto por su ID y retorna el gasto eliminado."""
        return self._repo.eliminar(gasto_id)

    def listar_gastos(self, categoria: Optional[str] = None) -> List[Gasto]:
        """Lista todos los gastos o filtra por categoría si se indica."""
        if categoria is None:
            return self._repo.listar_todos()
        self._validar_categoria(categoria)
        return self._repo.listar_por_categoria(categoria)

    def resumen_por_categoria(self) -> Dict[str, float]:
        """Retorna la suma de gastos agrupada por categoría, de mayor a menor."""
        resumen = self._repo.suma_por_categoria()
        return dict(sorted(resumen.items(), key=lambda x: x[1], reverse=True))

    def total_general(self) -> float:
        """Retorna el total acumulado de todos los gastos."""
        return self._repo.total_general()

    # ── Validaciones privadas ──────────────────────────────────────────

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

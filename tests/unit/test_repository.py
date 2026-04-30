"""
test_repository.py
CICLO TDD — Capa de acceso a datos con SQLAlchemy ORM.

Valida que las operaciones del repositorio funcionan correctamente
sobre SQLite en memoria. Cada test verifica un comportamiento ORM específico.
"""

import pytest
from src.models import Gasto
from src.exceptions import GastoNoEncontradoError, DatabaseError


class TestGuardar:
    """Kata TDD 1 — Persistencia de un nuevo gasto."""

    def test_guardar_asigna_id_autoincremental(self, repositorio):
        """RED: sin ORM configurado, el ID no se asigna."""
        gasto = Gasto(descripcion="Pan", monto=3.0, categoria="alimentacion", fecha="2025-01-01")
        guardado = repositorio.guardar(gasto)
        assert guardado.id is not None
        assert guardado.id >= 1

    def test_guardar_dos_gastos_tienen_ids_distintos(self, repositorio):
        """GREEN: SQLAlchemy asigna IDs únicos y crecientes."""
        g1 = Gasto(descripcion="Café", monto=4.0, categoria="alimentacion", fecha="2025-01-01")
        g2 = Gasto(descripcion="Agua", monto=2.0, categoria="alimentacion", fecha="2025-01-01")
        r1 = repositorio.guardar(g1)
        r2 = repositorio.guardar(g2)
        assert r1.id != r2.id

    def test_guardar_retorna_misma_instancia_actualizada(self, repositorio):
        """REFACTOR: refresh garantiza que el objeto refleje el estado de la BD."""
        gasto = Gasto(descripcion="Libro", monto=45.0, categoria="educacion", fecha="2025-01-01")
        resultado = repositorio.guardar(gasto)
        assert resultado is gasto


class TestBuscarPorId:
    """Kata TDD 2 — Búsqueda por clave primaria."""

    def test_buscar_id_existente_retorna_gasto(self, repositorio):
        gasto = Gasto(descripcion="Taxi", monto=25.0, categoria="transporte", fecha="2025-01-01")
        guardado = repositorio.guardar(gasto)
        encontrado = repositorio.buscar_por_id(guardado.id)
        assert encontrado.descripcion == "Taxi"

    def test_buscar_id_inexistente_lanza_excepcion(self, repositorio):
        """Edge case: ID que no existe en la BD."""
        with pytest.raises(GastoNoEncontradoError) as exc_info:
            repositorio.buscar_por_id(99999)
        assert "99999" in str(exc_info.value)


class TestListarTodos:
    """Kata TDD 3 — Consulta de todos los registros."""

    def test_listar_todos_retorna_lista_vacia_en_bd_nueva(self, repositorio):
        assert repositorio.listar_todos() == []

    def test_listar_todos_retorna_todos_los_gastos_guardados(self, repositorio):
        for i in range(5):
            repositorio.guardar(
                Gasto(descripcion=f"Gasto {i}", monto=float(i + 1),
                      categoria="otros", fecha="2025-01-01")
            )
        resultado = repositorio.listar_todos()
        assert len(resultado) == 5

    def test_listar_todos_retorna_instancias_de_gasto(self, repositorio):
        repositorio.guardar(
            Gasto(descripcion="Test", monto=10.0, categoria="otros", fecha="2025-01-01")
        )
        resultado = repositorio.listar_todos()
        assert all(isinstance(g, Gasto) for g in resultado)


class TestListarPorCategoria:
    """Kata TDD 4 — Consulta filtrada por categoría (query ORM)."""

    def test_filtrar_retorna_solo_gastos_de_esa_categoria(self, repositorio):
        repositorio.guardar(Gasto(descripcion="A", monto=10.0, categoria="salud", fecha="2025-01-01"))
        repositorio.guardar(Gasto(descripcion="B", monto=20.0, categoria="salud", fecha="2025-01-01"))
        repositorio.guardar(Gasto(descripcion="C", monto=30.0, categoria="hogar", fecha="2025-01-01"))
        resultado = repositorio.listar_por_categoria("salud")
        assert len(resultado) == 2
        assert all(g.categoria == "salud" for g in resultado)

    def test_filtrar_categoria_sin_gastos_retorna_lista_vacia(self, repositorio):
        repositorio.guardar(Gasto(descripcion="Bus", monto=3.0, categoria="transporte", fecha="2025-01-01"))
        resultado = repositorio.listar_por_categoria("salud")
        assert resultado == []


class TestEliminar:
    """Kata TDD 5 — Eliminación de un registro ORM."""

    def test_eliminar_gasto_lo_remueve_de_la_bd(self, repositorio):
        gasto = repositorio.guardar(
            Gasto(descripcion="Borrar", monto=5.0, categoria="otros", fecha="2025-01-01")
        )
        gasto_id = gasto.id
        repositorio.eliminar(gasto_id)
        with pytest.raises(GastoNoEncontradoError):
            repositorio.buscar_por_id(gasto_id)

    def test_eliminar_retorna_gasto_eliminado(self, repositorio):
        gasto = repositorio.guardar(
            Gasto(descripcion="Eliminar", monto=7.0, categoria="otros", fecha="2025-01-01")
        )
        eliminado = repositorio.eliminar(gasto.id)
        assert eliminado.descripcion == "Eliminar"

    def test_eliminar_id_inexistente_lanza_excepcion(self, repositorio):
        with pytest.raises(GastoNoEncontradoError):
            repositorio.eliminar(8888)


class TestAgregaciones:
    """Kata TDD 6 — Funciones de agregación SQL vía ORM."""

    def test_suma_por_categoria_calcula_correctamente(self, repositorio):
        """Verifica que func.sum() agrupa y suma correctamente por categoria."""
        repositorio.guardar(Gasto(descripcion="A", monto=10.0, categoria="hogar", fecha="2025-01-01"))
        repositorio.guardar(Gasto(descripcion="B", monto=15.0, categoria="hogar", fecha="2025-01-01"))
        repositorio.guardar(Gasto(descripcion="C", monto=5.0, categoria="salud", fecha="2025-01-01"))
        resumen = repositorio.suma_por_categoria()
        assert resumen["hogar"] == 25.0
        assert resumen["salud"] == 5.0

    def test_total_general_suma_todos_los_montos(self, repositorio):
        repositorio.guardar(Gasto(descripcion="X", monto=100.0, categoria="hogar", fecha="2025-01-01"))
        repositorio.guardar(Gasto(descripcion="Y", monto=50.0, categoria="salud", fecha="2025-01-01"))
        assert repositorio.total_general() == 150.0

    def test_total_general_cero_en_bd_vacia(self, repositorio):
        assert repositorio.total_general() == 0.0

    def test_suma_redondea_a_dos_decimales(self, repositorio):
        """Edge case: acumulación de floats debe redondearse correctamente."""
        repositorio.guardar(Gasto(descripcion="A", monto=0.1, categoria="otros", fecha="2025-01-01"))
        repositorio.guardar(Gasto(descripcion="B", monto=0.2, categoria="otros", fecha="2025-01-01"))
        resumen = repositorio.suma_por_categoria()
        assert resumen["otros"] == 0.3

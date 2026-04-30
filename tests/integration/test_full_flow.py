"""
test_full_flow.py
PRUEBAS DE INTEGRACIÓN — Flujo completo de la aplicación.

A diferencia de los tests unitarios (que prueban cada componente aislado),
estos tests verifican que las capas trabajen correctamente juntas:
Servicio → Repositorio → SQLAlchemy ORM → SQLite en memoria.
"""

import pytest
from src.exceptions import GastoNoEncontradoError, CategoriaInvalidaError


class TestFlujoCompletoRegistroYConsulta:
    """Integración: registrar gastos y consultarlos de extremo a extremo."""

    def test_registrar_y_listar_multiples_gastos(self, servicio):
        """El servicio coordina correctamente registro y consulta."""
        servicio.agregar_gasto("Desayuno", 15.0, "alimentacion")
        servicio.agregar_gasto("Bus", 3.0, "transporte")
        servicio.agregar_gasto("Cine", 30.0, "entretenimiento")

        todos = servicio.listar_gastos()
        assert len(todos) == 3

    def test_registrar_y_filtrar_por_categoria(self, servicio):
        """El filtro pasa por el servicio y el repositorio correctamente."""
        servicio.agregar_gasto("Pollo", 25.0, "alimentacion")
        servicio.agregar_gasto("Sopa", 18.0, "alimentacion")
        servicio.agregar_gasto("Taxi", 40.0, "transporte")

        alimentacion = servicio.listar_gastos("alimentacion")
        assert len(alimentacion) == 2

    def test_registrar_y_eliminar_reduce_conteo(self, servicio):
        g1 = servicio.agregar_gasto("A", 10.0, "otros")
        g2 = servicio.agregar_gasto("B", 20.0, "otros")

        servicio.eliminar_gasto(g1.id)
        restantes = servicio.listar_gastos()
        assert len(restantes) == 1
        assert restantes[0].id == g2.id


class TestFlujoCompletoEstadisticas:
    """Integración: cálculos estadísticos con múltiples registros."""

    def test_resumen_correcto_con_multiples_categorias(self, servicio):
        servicio.agregar_gasto("Arroz", 10.0, "alimentacion")
        servicio.agregar_gasto("Pan", 5.0, "alimentacion")
        servicio.agregar_gasto("Metro", 3.0, "transporte")
        servicio.agregar_gasto("Curso", 200.0, "educacion")

        resumen = servicio.resumen_por_categoria()
        assert resumen["alimentacion"] == 15.0
        assert resumen["transporte"] == 3.0
        assert resumen["educacion"] == 200.0

    def test_total_general_correcto_tras_eliminaciones(self, servicio):
        g1 = servicio.agregar_gasto("A", 100.0, "hogar")
        g2 = servicio.agregar_gasto("B", 50.0, "hogar")
        servicio.agregar_gasto("C", 30.0, "salud")

        servicio.eliminar_gasto(g1.id)
        assert servicio.total_general() == 80.0

    def test_resumen_esta_ordenado_mayor_a_menor(self, servicio):
        servicio.agregar_gasto("Uber", 15.0, "transporte")
        servicio.agregar_gasto("Diploma", 800.0, "educacion")
        servicio.agregar_gasto("Comida", 120.0, "alimentacion")

        valores = list(servicio.resumen_por_categoria().values())
        assert valores == sorted(valores, reverse=True)


class TestFlujoCompletoRobustez:
    """Integración: el sistema maneja errores sin corromper el estado."""

    def test_error_en_registro_no_afecta_gastos_previos(self, servicio):
        """Un registro fallido no debe alterar los datos existentes."""
        servicio.agregar_gasto("Valido", 50.0, "hogar")

        with pytest.raises(Exception):
            servicio.agregar_gasto("Invalido", -10.0, "hogar")

        gastos = servicio.listar_gastos()
        assert len(gastos) == 1
        assert gastos[0].descripcion == "Valido"

    def test_eliminar_id_inexistente_no_afecta_bd(self, servicio):
        """Intentar eliminar un ID inexistente no borra datos válidos."""
        g = servicio.agregar_gasto("Persistente", 100.0, "educacion")

        with pytest.raises(GastoNoEncontradoError):
            servicio.eliminar_gasto(99999)

        encontrado = servicio.listar_gastos()
        assert len(encontrado) == 1

    def test_categoria_invalida_no_registra_gasto_parcial(self, servicio):
        """La validación ocurre antes de tocar la BD (fail fast)."""
        with pytest.raises(CategoriaInvalidaError):
            servicio.agregar_gasto("Test", 50.0, "lujo_extremo")
        assert servicio.listar_gastos() == []

    def test_multiples_eliminaciones_secuenciales(self, servicio):
        """Eliminar varios gastos en secuencia funciona correctamente."""
        gastos = [servicio.agregar_gasto(f"G{i}", 10.0 * i, "otros") for i in range(1, 6)]
        for g in gastos[:3]:
            servicio.eliminar_gasto(g.id)
        assert len(servicio.listar_gastos()) == 2

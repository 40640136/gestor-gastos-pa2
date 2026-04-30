"""
test_service.py
CICLO TDD — Validaciones y lógica de negocio en ServicioGastos.

Cada clase agrupa una Kata TDD sobre un comportamiento específico.
Los métodos siguen el patrón: test_<comportamiento>_<condicion>_<resultado_esperado>
"""

import pytest
from src.exceptions import (
    MontoInvalidoError,
    CategoriaInvalidaError,
    DescripcionVaciaError,
    GastoNoEncontradoError,
)


class TestAgregarGasto:
    """Kata TDD 1 — Registro de un nuevo gasto."""

    def test_agregar_gasto_valido_retorna_gasto_con_id(self, servicio, gasto_valido_data):
        """RED → GREEN: agregar un gasto válido debe retornar instancia con ID."""
        gasto = servicio.agregar_gasto(**gasto_valido_data)
        assert gasto.id is not None
        assert gasto.id > 0

    def test_agregar_gasto_persiste_descripcion_sin_espacios(self, servicio):
        """REFACTOR: strip() elimina espacios al inicio y al final."""
        gasto = servicio.agregar_gasto("  Café con leche  ", 8.50, "alimentacion")
        assert gasto.descripcion == "Café con leche"

    def test_agregar_gasto_persiste_categoria_en_minusculas(self, servicio):
        """REFACTOR: categoría normalizada a minúsculas."""
        gasto = servicio.agregar_gasto("Taxi", 20.0, "TRANSPORTE")
        assert gasto.categoria == "transporte"

    def test_agregar_gasto_redondea_monto_a_dos_decimales(self, servicio):
        """REFACTOR: round() garantiza máximo 2 decimales en el monto persistido."""
        gasto = servicio.agregar_gasto("Postre", 12.549, "alimentacion")
        assert gasto.monto == 12.55

    def test_agregar_gasto_con_fecha_personalizada(self, servicio):
        gasto = servicio.agregar_gasto("Vacuna", 150.0, "salud", fecha="2025-01-15")
        assert gasto.fecha == "2025-01-15"


class TestValidacionDescripcion:
    """Kata TDD 2 — Validación de la descripción."""

    def test_descripcion_vacia_lanza_excepcion(self, servicio):
        """RED: sin validación, un gasto con descripción vacía se guardaría."""
        with pytest.raises(DescripcionVaciaError):
            servicio.agregar_gasto("", 10.0, "alimentacion")

    def test_descripcion_solo_espacios_lanza_excepcion(self, servicio):
        with pytest.raises(DescripcionVaciaError):
            servicio.agregar_gasto("   ", 10.0, "alimentacion")

    def test_descripcion_ninguna_lanza_excepcion(self, servicio):
        with pytest.raises(DescripcionVaciaError):
            servicio.agregar_gasto(None, 10.0, "alimentacion")

    def test_descripcion_un_caracter_es_valida(self, servicio):
        """Edge case: la descripción mínima válida es un solo carácter."""
        gasto = servicio.agregar_gasto("A", 5.0, "otros")
        assert gasto.descripcion == "A"


class TestValidacionMonto:
    """Kata TDD 3 — Validación del monto."""

    def test_monto_negativo_lanza_excepcion(self, servicio):
        """RED: un monto negativo no debe ser aceptado."""
        with pytest.raises(MontoInvalidoError) as exc_info:
            servicio.agregar_gasto("Test", -1.0, "otros")
        assert "-1.0" in str(exc_info.value)

    def test_monto_cero_lanza_excepcion(self, servicio):
        """Edge case: cero no representa un gasto real."""
        with pytest.raises(MontoInvalidoError):
            servicio.agregar_gasto("Test", 0.0, "otros")

    def test_monto_muy_pequeno_positivo_es_valido(self, servicio):
        """Edge case: cualquier monto positivo, por pequeño que sea, es válido."""
        gasto = servicio.agregar_gasto("Propina", 0.01, "otros")
        assert gasto.monto == 0.01

    def test_monto_muy_grande_es_valido(self, servicio):
        """Edge case: no existe límite superior para el monto."""
        gasto = servicio.agregar_gasto("Auto", 50000.0, "transporte")
        assert gasto.monto == 50000.0


class TestValidacionCategoria:
    """Kata TDD 4 — Validación de la categoría."""

    def test_categoria_invalida_lanza_excepcion_con_mensaje_descriptivo(self, servicio):
        """RED: una categoría no registrada debe rechazarse."""
        with pytest.raises(CategoriaInvalidaError) as exc_info:
            servicio.agregar_gasto("Test", 10.0, "lujo")
        assert "lujo" in str(exc_info.value)

    def test_todas_las_categorias_validas_son_aceptadas(self, servicio):
        """GREEN: cada categoría del conjunto debe funcionar correctamente."""
        from src.models import CATEGORIAS_VALIDAS
        for i, categoria in enumerate(CATEGORIAS_VALIDAS):
            gasto = servicio.agregar_gasto(f"Gasto {i}", float(i + 1), categoria)
            assert gasto.categoria == categoria

    def test_categoria_invalida_contiene_opciones_en_mensaje(self, servicio):
        """REFACTOR: el mensaje de error debe guiar al usuario."""
        with pytest.raises(CategoriaInvalidaError) as exc_info:
            servicio.agregar_gasto("Test", 10.0, "fitness")
        mensaje = str(exc_info.value)
        assert "alimentacion" in mensaje or "salud" in mensaje


class TestListarGastos:
    """Kata TDD 5 — Listado y filtrado de gastos."""

    def test_listar_gastos_retorna_lista_vacia_sin_datos(self, servicio):
        """RED: una BD vacía debe retornar lista vacía, no None."""
        resultado = servicio.listar_gastos()
        assert resultado == []

    def test_listar_gastos_retorna_todos_los_registrados(self, servicio):
        """GREEN: después de agregar N gastos, se listan todos."""
        servicio.agregar_gasto("Café", 5.0, "alimentacion")
        servicio.agregar_gasto("Bus", 3.0, "transporte")
        servicio.agregar_gasto("Cine", 25.0, "entretenimiento")
        resultado = servicio.listar_gastos()
        assert len(resultado) == 3

    def test_listar_por_categoria_filtra_correctamente(self, servicio):
        """GREEN: el filtro devuelve solo los gastos de esa categoría."""
        servicio.agregar_gasto("Desayuno", 15.0, "alimentacion")
        servicio.agregar_gasto("Almuerzo", 35.0, "alimentacion")
        servicio.agregar_gasto("Metro", 2.5, "transporte")
        resultado = servicio.listar_gastos("alimentacion")
        assert len(resultado) == 2
        assert all(g.categoria == "alimentacion" for g in resultado)

    def test_listar_por_categoria_invalida_lanza_excepcion(self, servicio):
        with pytest.raises(CategoriaInvalidaError):
            servicio.listar_gastos("vacaciones")


class TestEliminarGasto:
    """Kata TDD 6 — Eliminación de un gasto."""

    def test_eliminar_gasto_existente_lo_remueve_de_la_bd(self, servicio):
        """RED → GREEN: el gasto eliminado no debe aparecer en el listado."""
        gasto = servicio.agregar_gasto("Taxi", 30.0, "transporte")
        gasto_id = gasto.id
        servicio.eliminar_gasto(gasto_id)
        assert len(servicio.listar_gastos()) == 0

    def test_eliminar_gasto_retorna_el_gasto_eliminado(self, servicio):
        """REFACTOR: la operación retorna la entidad para confirmar al usuario."""
        gasto = servicio.agregar_gasto("Cena", 80.0, "alimentacion")
        eliminado = servicio.eliminar_gasto(gasto.id)
        assert eliminado.descripcion == "Cena"

    def test_eliminar_gasto_inexistente_lanza_excepcion(self, servicio):
        """Edge case: IDs que no existen deben lanzar excepción específica."""
        with pytest.raises(GastoNoEncontradoError) as exc_info:
            servicio.eliminar_gasto(9999)
        assert "9999" in str(exc_info.value)


class TestResumenYTotales:
    """Kata TDD 7 — Estadísticas y resumen financiero."""

    def test_total_general_cero_sin_gastos(self, servicio):
        assert servicio.total_general() == 0.0

    def test_total_general_suma_todos_los_montos(self, servicio):
        servicio.agregar_gasto("A", 10.0, "hogar")
        servicio.agregar_gasto("B", 20.0, "hogar")
        servicio.agregar_gasto("C", 5.50, "salud")
        assert servicio.total_general() == 35.50

    def test_resumen_por_categoria_agrupa_correctamente(self, servicio):
        servicio.agregar_gasto("Desayuno", 15.0, "alimentacion")
        servicio.agregar_gasto("Almuerzo", 25.0, "alimentacion")
        servicio.agregar_gasto("Bus", 3.0, "transporte")
        resumen = servicio.resumen_por_categoria()
        assert resumen["alimentacion"] == 40.0
        assert resumen["transporte"] == 3.0

    def test_resumen_ordenado_de_mayor_a_menor(self, servicio):
        """REFACTOR: el resumen debe estar ordenado para facilitar lectura."""
        servicio.agregar_gasto("Transporte barato", 5.0, "transporte")
        servicio.agregar_gasto("Educacion cara", 500.0, "educacion")
        servicio.agregar_gasto("Comida media", 50.0, "alimentacion")
        resumen = servicio.resumen_por_categoria()
        valores = list(resumen.values())
        assert valores == sorted(valores, reverse=True)

    def test_resumen_vacio_sin_gastos(self, servicio):
        resumen = servicio.resumen_por_categoria()
        assert resumen == {}

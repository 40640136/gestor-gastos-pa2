"""
test_models.py
CICLO TDD — Fase de diseño del modelo de datos.

Kata TDD iterativa:
  RED   → el test falla porque el modelo no existe
  GREEN → se crea el modelo mínimo para pasar el test
  REFACTOR → se agregan constraints y métodos auxiliares

Cada clase de test representa una iteración del ciclo Red→Green→Refactor.
"""

import pytest
from src.models import Gasto, CATEGORIAS_VALIDAS


class TestGastoCreacion:
    """TDD Iteración 1 — Creación básica de un gasto."""

    def test_gasto_se_crea_con_atributos_correctos(self):
        """RED: antes de crear el modelo, este test falla con ImportError."""
        gasto = Gasto(descripcion="Café", monto=5.0, categoria="alimentacion")
        assert gasto.descripcion == "Café"
        assert gasto.monto == 5.0
        assert gasto.categoria == "alimentacion"

    def test_gasto_tiene_fecha_por_defecto(self):
        """GREEN: el default de fecha se asigna en el momento de instanciación."""
        gasto = Gasto(descripcion="Taxi", monto=15.0, categoria="transporte")
        assert gasto.fecha is not None
        assert len(gasto.fecha) == 10  # formato YYYY-MM-DD

    def test_gasto_sin_id_antes_de_persistir(self):
        """Un gasto nuevo no tiene ID hasta ser guardado en la BD."""
        gasto = Gasto(descripcion="Medicina", monto=45.0, categoria="salud")
        assert gasto.id is None


class TestGastoToDict:
    """TDD Iteración 2 — Serialización a diccionario."""

    def test_to_dict_incluye_todos_los_campos(self):
        """RED: to_dict no existe → AttributeError."""
        gasto = Gasto(descripcion="Libro", monto=89.90, categoria="educacion")
        resultado = gasto.to_dict()
        assert "id" in resultado
        assert "descripcion" in resultado
        assert "monto" in resultado
        assert "categoria" in resultado
        assert "fecha" in resultado

    def test_to_dict_valores_correctos(self):
        """GREEN: los valores del dict coinciden con los atributos del objeto."""
        gasto = Gasto(descripcion="Libro", monto=89.90, categoria="educacion", fecha="2025-04-01")
        resultado = gasto.to_dict()
        assert resultado["descripcion"] == "Libro"
        assert resultado["monto"] == 89.90
        assert resultado["categoria"] == "educacion"
        assert resultado["fecha"] == "2025-04-01"


class TestGastoEquality:
    """TDD Iteración 3 — Comparación de igualdad."""

    def test_dos_gastos_con_mismo_id_son_iguales(self):
        """REFACTOR: __eq__ implementado por ID."""
        gasto_a = Gasto(descripcion="Cine", monto=25.0, categoria="entretenimiento")
        gasto_b = Gasto(descripcion="Cine VIP", monto=40.0, categoria="entretenimiento")
        gasto_a.id = 1
        gasto_b.id = 1
        assert gasto_a == gasto_b

    def test_dos_gastos_con_diferente_id_no_son_iguales(self):
        gasto_a = Gasto(descripcion="Cine", monto=25.0, categoria="entretenimiento")
        gasto_b = Gasto(descripcion="Cine", monto=25.0, categoria="entretenimiento")
        gasto_a.id = 1
        gasto_b.id = 2
        assert gasto_a != gasto_b

    def test_gasto_no_es_igual_a_no_gasto(self):
        gasto = Gasto(descripcion="Cine", monto=25.0, categoria="entretenimiento")
        gasto.id = 1
        assert gasto != {"id": 1}


class TestCategoriasValidas:
    """TDD Iteración 4 — Verificar el conjunto de categorías."""

    def test_categorias_validas_no_esta_vacio(self):
        assert len(CATEGORIAS_VALIDAS) > 0

    def test_categorias_esperadas_existen(self):
        categorias_esperadas = {
            "alimentacion", "transporte", "salud",
            "entretenimiento", "educacion", "hogar", "otros"
        }
        assert categorias_esperadas == CATEGORIAS_VALIDAS

    def test_categorias_validas_es_inmutable(self):
        """REFACTOR: frozenset garantiza inmutabilidad."""
        assert isinstance(CATEGORIAS_VALIDAS, frozenset)


class TestGastoRepr:
    """TDD Iteración 5 — Representación en cadena."""

    def test_repr_contiene_informacion_clave(self):
        gasto = Gasto(descripcion="Netflix", monto=45.0, categoria="entretenimiento")
        gasto.id = 7
        representacion = repr(gasto)
        assert "7" in representacion
        assert "Netflix" in representacion
        assert "45.0" in representacion

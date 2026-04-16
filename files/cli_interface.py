"""
ui/cli_interface.py
Interfaz de línea de comandos para la aplicación de gestión de gastos.
Gestiona la presentación y la interacción con el usuario.
"""

from typing import List

from models.expense import Gasto, CATEGORIAS_VALIDAS
from services.expense_service import ServicioGastos
from exceptions import GestionGastosError


SEPARADOR = "=" * 55
SEPARADOR_FINO = "-" * 55


class InterfazCLI:
    """Controla el flujo de la interfaz de línea de comandos."""

    MENU_PRINCIPAL = """
{sep}
   GESTOR DE GASTOS PERSONALES
{sep}
  1. Registrar nuevo gasto
  2. Ver todos los gastos
  3. Ver gastos por categoría
  4. Eliminar un gasto
  5. Resumen por categoría
  6. Salir
{sep}""".format(sep=SEPARADOR)

    def __init__(self):
        self._servicio = ServicioGastos()

    def ejecutar(self) -> None:
        """Inicia el bucle principal de la aplicación."""
        print("\n¡Bienvenido al Gestor de Gastos Personales!")
        while True:
            print(self.MENU_PRINCIPAL)
            opcion = input("Selecciona una opción: ").strip()
            self._procesar_opcion(opcion)

    # ------------------------------------------------------------------ #
    #  Enrutador de opciones                                               #
    # ------------------------------------------------------------------ #

    def _procesar_opcion(self, opcion: str) -> None:
        acciones = {
            "1": self._registrar_gasto,
            "2": self._mostrar_todos,
            "3": self._mostrar_por_categoria,
            "4": self._eliminar_gasto,
            "5": self._mostrar_resumen,
            "6": self._salir,
        }
        accion = acciones.get(opcion)
        if accion:
            accion()
        else:
            print("⚠  Opción no válida. Ingresa un número del 1 al 6.")

    # ------------------------------------------------------------------ #
    #  Handlers de cada opción                                             #
    # ------------------------------------------------------------------ #

    def _registrar_gasto(self) -> None:
        print(f"\n{SEPARADOR_FINO}\n  REGISTRAR NUEVO GASTO\n{SEPARADOR_FINO}")
        try:
            descripcion = input("Descripción: ")
            monto = self._leer_monto()
            categoria = self._leer_categoria()
            gasto = self._servicio.agregar_gasto(descripcion, monto, categoria)
            print(f"\n✔  Gasto registrado correctamente (ID: {gasto.gasto_id})")
        except GestionGastosError as error:
            print(f"\n✘  Error: {error}")

    def _mostrar_todos(self) -> None:
        print(f"\n{SEPARADOR_FINO}\n  LISTA DE GASTOS\n{SEPARADOR_FINO}")
        gastos = self._servicio.listar_gastos()
        if not gastos:
            print("No hay gastos registrados.")
            return
        self._imprimir_tabla(gastos)
        print(f"\nTotal: S/ {self._servicio.total_general():.2f}")

    def _mostrar_por_categoria(self) -> None:
        print(f"\n{SEPARADOR_FINO}\n  FILTRAR POR CATEGORÍA\n{SEPARADOR_FINO}")
        self._imprimir_categorias()
        try:
            categoria = input("Categoría: ").strip()
            gastos = self._servicio.listar_gastos(categoria)
            if not gastos:
                print(f"No hay gastos en la categoría '{categoria}'.")
                return
            self._imprimir_tabla(gastos)
        except GestionGastosError as error:
            print(f"\n✘  Error: {error}")

    def _eliminar_gasto(self) -> None:
        print(f"\n{SEPARADOR_FINO}\n  ELIMINAR GASTO\n{SEPARADOR_FINO}")
        try:
            gasto_id = int(input("ID del gasto a eliminar: "))
            gasto = self._servicio.eliminar_gasto(gasto_id)
            print(f"\n✔  Gasto '{gasto.descripcion}' eliminado correctamente.")
        except ValueError:
            print("\n✘  Error: El ID debe ser un número entero.")
        except GestionGastosError as error:
            print(f"\n✘  Error: {error}")

    def _mostrar_resumen(self) -> None:
        print(f"\n{SEPARADOR_FINO}\n  RESUMEN POR CATEGORÍA\n{SEPARADOR_FINO}")
        resumen = self._servicio.resumen_por_categoria()
        if not resumen:
            print("No hay gastos registrados.")
            return
        for categoria, total in resumen.items():
            print(f"  {categoria.capitalize():<18} S/ {total:>8.2f}")
        print(SEPARADOR_FINO)
        print(f"  {'TOTAL':<18} S/ {self._servicio.total_general():>8.2f}")

    @staticmethod
    def _salir() -> None:
        print("\nHasta pronto. ¡Cuida tus finanzas!\n")
        raise SystemExit(0)

    # ------------------------------------------------------------------ #
    #  Utilidades de entrada y presentación                                #
    # ------------------------------------------------------------------ #

    def _leer_monto(self) -> float:
        """Solicita un monto al usuario con reintento ante errores de formato."""
        while True:
            try:
                valor = input("Monto (S/): ")
                return float(valor)
            except ValueError:
                print("  ⚠  Ingresa un número válido (ej: 25.50).")

    def _leer_categoria(self) -> str:
        """Muestra las categorías disponibles y solicita una al usuario."""
        self._imprimir_categorias()
        return input("Categoría: ").strip()

    @staticmethod
    def _imprimir_categorias() -> None:
        categorias = sorted(CATEGORIAS_VALIDAS)
        print("  Categorías: " + " | ".join(c.capitalize() for c in categorias))

    @staticmethod
    def _imprimir_tabla(gastos: List[Gasto]) -> None:
        print(f"\n  {'ID':<5} {'Fecha':<12} {'Categoría':<16} {'Monto':>10}  Descripción")
        print(f"  {'-'*5} {'-'*12} {'-'*16} {'-'*10}  {'-'*20}")
        for g in gastos:
            print(
                f"  {g.gasto_id:<5} {g.fecha:<12} {g.categoria.capitalize():<16}"
                f" S/{g.monto:>8.2f}  {g.descripcion}"
            )

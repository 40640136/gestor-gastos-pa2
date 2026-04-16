"""
exceptions.py
Excepciones personalizadas para el sistema de gestión de gastos.
"""


class GestionGastosError(Exception):
    """Excepción base para el sistema de gestión de gastos."""
    pass


class MontoInvalidoError(GestionGastosError):
    """Se lanza cuando el monto ingresado no es válido (negativo o cero)."""

    def __init__(self, monto):
        super().__init__(f"El monto '{monto}' no es válido. Debe ser un número positivo mayor que cero.")
        self.monto = monto


class CategoriaInvalidaError(GestionGastosError):
    """Se lanza cuando la categoría ingresada no existe en el sistema."""

    def __init__(self, categoria, categorias_validas):
        validas = ", ".join(categorias_validas)
        super().__init__(f"La categoría '{categoria}' no es válida. Opciones: {validas}.")
        self.categoria = categoria


class DescripcionVaciaError(GestionGastosError):
    """Se lanza cuando la descripción del gasto está vacía o contiene solo espacios."""

    def __init__(self):
        super().__init__("La descripción no puede estar vacía.")


class GastoNoEncontradoError(GestionGastosError):
    """Se lanza cuando se intenta acceder a un gasto con un ID inexistente."""

    def __init__(self, gasto_id):
        super().__init__(f"No se encontró ningún gasto con el ID '{gasto_id}'.")
        self.gasto_id = gasto_id


class ArchivoCorruptoError(GestionGastosError):
    """Se lanza cuando el archivo de datos no puede ser leído o está dañado."""

    def __init__(self, ruta, detalle=""):
        mensaje = f"El archivo de datos '{ruta}' está corrupto o no puede leerse."
        if detalle:
            mensaje += f" Detalle: {detalle}"
        super().__init__(mensaje)
        self.ruta = ruta

"""
exceptions.py
Jerarquía de excepciones personalizadas del dominio de gestión de gastos.
Todas heredan de GestionGastosError para facilitar el manejo genérico.
"""


class GestionGastosError(Exception):
    """Excepción base del dominio. Captura todos los errores de negocio."""
    pass


class MontoInvalidoError(GestionGastosError):
    """Monto negativo o igual a cero."""

    def __init__(self, monto):
        super().__init__(
            f"El monto '{monto}' no es valido. Debe ser un numero positivo mayor que cero."
        )
        self.monto = monto


class CategoriaInvalidaError(GestionGastosError):
    """Categoría no reconocida por el sistema."""

    def __init__(self, categoria, categorias_validas):
        validas = ", ".join(sorted(categorias_validas))
        super().__init__(
            f"La categoria '{categoria}' no es valida. Opciones disponibles: {validas}."
        )
        self.categoria = categoria


class DescripcionVaciaError(GestionGastosError):
    """Descripción vacía o compuesta solo por espacios."""

    def __init__(self):
        super().__init__("La descripcion no puede estar vacia.")


class GastoNoEncontradoError(GestionGastosError):
    """ID de gasto inexistente en la base de datos."""

    def __init__(self, gasto_id):
        super().__init__(f"No se encontro ningun gasto con el ID '{gasto_id}'.")
        self.gasto_id = gasto_id


class DatabaseError(GestionGastosError):
    """Error al interactuar con la base de datos."""

    def __init__(self, operacion, detalle=""):
        mensaje = f"Error al ejecutar la operacion '{operacion}' en la base de datos."
        if detalle:
            mensaje += f" Detalle: {detalle}"
        super().__init__(mensaje)
        self.operacion = operacion

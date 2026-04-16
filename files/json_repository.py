"""
storage/json_repository.py
Responsable de la persistencia de datos en formato JSON.
Implementa el patrón Repository para desacoplar el almacenamiento de la lógica de negocio.
"""

import json
import os
from typing import List

from models.expense import Gasto
from exceptions import ArchivoCorruptoError


RUTA_DATOS = "gastos.json"


class RepositorioGastos:
    """Gestiona la lectura y escritura de gastos en un archivo JSON."""

    def __init__(self, ruta: str = RUTA_DATOS):
        self._ruta = ruta

    def cargar_todos(self) -> List[Gasto]:
        """Carga todos los gastos desde el archivo JSON."""
        if not os.path.exists(self._ruta):
            return []

        try:
            with open(self._ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
            return [Gasto.from_dict(item) for item in datos]
        except json.JSONDecodeError as error:
            raise ArchivoCorruptoError(self._ruta, str(error)) from error
        except (KeyError, TypeError) as error:
            raise ArchivoCorruptoError(self._ruta, f"Estructura inesperada: {error}") from error

    def guardar_todos(self, gastos: List[Gasto]) -> None:
        """Persiste la lista completa de gastos en el archivo JSON."""
        try:
            with open(self._ruta, "w", encoding="utf-8") as archivo:
                json.dump([g.to_dict() for g in gastos], archivo, ensure_ascii=False, indent=2)
        except OSError as error:
            raise ArchivoCorruptoError(self._ruta, f"No se pudo escribir: {error}") from error

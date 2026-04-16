"""
main.py
Punto de entrada de la aplicación Gestor de Gastos Personales.

Uso:
    python main.py

Desarrollado con metodología ágil (Scrum - Sprint 1).
Código generado y revisado con asistencia de IA generativa (Claude - Anthropic).
"""

import sys
import os

# Para Permitir importar módulos desde el directorio raíz del proyecto
sys.path.insert(0, os.path.dirname(__file__))

from ui.cli_interface import InterfazCLI
from exceptions import ArchivoCorruptoError


def main() -> None:
    """Inicializa y ejecuta la aplicación de gestión de gastos."""
    try:
        app = InterfazCLI()
        app.ejecutar()
    except ArchivoCorruptoError as error:
        print(f"\n[ERROR CRÍTICO] {error}")
        print("Por favor, respalde y elimine el archivo 'gastos.json' para reiniciar.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nAplicación interrumpida por el usuario.")
        sys.exit(0)


if __name__ == "__main__":
    main()

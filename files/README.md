# Gestor de Gastos Personales 💰

Aplicación de consola para registrar y analizar gastos personales, desarrollada con Python usando principios de código limpio y metodología Scrum.

## Estructura del proyecto

```
gestion_gastos/
├── main.py                      # Punto de entrada
├── exceptions.py                # Excepciones personalizadas
├── gastos.json                  # Datos persistidos (se crea automáticamente)
├── models/
│   └── expense.py               # Modelo de datos Gasto
├── storage/
│   └── json_repository.py       # Persistencia en JSON
├── services/
│   └── expense_service.py       # Lógica de negocio y validaciones
└── ui/
    └── cli_interface.py         # Interfaz de línea de comandos
```

## Requisitos

- Python 3.8+
- Sin dependencias externas (solo biblioteca estándar)

## Ejecución

```bash
cd gestion_gastos
python main.py
```

## Funcionalidades

- ✅ Registrar gastos con descripción, monto y categoría
- ✅ Listar todos los gastos o filtrar por categoría
- ✅ Eliminar gastos por ID
- ✅ Ver resumen total por categoría
- ✅ Persistencia automática en JSON

## Categorías disponibles

`alimentacion` | `transporte` | `salud` | `entretenimiento` | `educacion` | `hogar` | `otros`

#cambio exclusivo para la rama develop

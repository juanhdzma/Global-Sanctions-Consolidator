#!/bin/bash

# Moverse al directorio del script (opcional)
cd "$(dirname "$0")"

# Activa el entorno virtual
source app/venv/bin/activate

# Ejecuta la aplicación
python "app/main.py"
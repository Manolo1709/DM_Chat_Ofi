"""Configuración de pytest: las pruebas no escriben en logs/errores.txt."""

import os

os.environ["LOG_ARCHIVO"] = "false"

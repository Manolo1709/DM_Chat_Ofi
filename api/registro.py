"""Registro de errores del servidor: por consola y, en local, en logs/errores.txt.

Solo se anota el motivo del fallo (por ejemplo, «el modelo no respondió a tiempo»),
nunca los datos del usuario ni la respuesta de la IA.
"""

import logging
import os
from pathlib import Path

RUTA_LOG = Path(__file__).resolve().parent.parent / "logs" / "errores.txt"
FORMATO = "%(asctime)s [%(levelname)s] %(message)s"


def crear_logger(nombre: str, ruta: Path | None = RUTA_LOG) -> logging.Logger:
    log = logging.getLogger(nombre)
    if log.handlers:
        return log

    log.setLevel(logging.INFO)
    log.propagate = False
    formato = logging.Formatter(FORMATO)

    consola = logging.StreamHandler()
    consola.setFormatter(formato)
    log.addHandler(consola)

    if ruta is not None:
        try:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            archivo = logging.FileHandler(ruta, encoding="utf-8")
            archivo.setLevel(logging.WARNING)
            archivo.setFormatter(formato)
            log.addHandler(archivo)
        except OSError as e:
            log.warning("No se puede escribir el archivo de errores: %s", e)

    return log


def archivo_activo() -> bool:
    # En Vercel el sistema de archivos es de solo lectura: allí solo hay consola.
    # LOG_ARCHIVO=false lo desactiva (lo usan las pruebas).
    return not os.getenv("VERCEL") and os.getenv("LOG_ARCHIVO", "true").lower() != "false"


logger = crear_logger("taberna", RUTA_LOG if archivo_activo() else None)

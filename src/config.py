"""Carga la configuración del entorno activo (dev, qa o prod)."""

import json
import os
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent


def cargar_config(entorno: str | None = None) -> dict:
    """Lee config/<entorno>.yaml. Si no se indica, usa RETAILMAX_ENTORNO o dev.

    RETAILMAX_RUTA_VENTAS cambia el archivo de datos sin tocar las reglas del entorno.
    El pipeline de CD lo usa para validar y entrenar la muestra con los umbrales de prod.
    """
    entorno = entorno or os.getenv("RETAILMAX_ENTORNO", "dev")
    ruta = RAIZ / "config" / f"{entorno}.yaml"
    with open(ruta, encoding="utf-8") as archivo:
        config = yaml.safe_load(archivo)
    if os.getenv("RETAILMAX_RUTA_VENTAS"):
        config["datos"]["ruta_ventas"] = os.environ["RETAILMAX_RUTA_VENTAS"]
    return config


def cargar_config_modelo() -> dict:
    """Lee los hiperparámetros del modelo desde config/modelo.json."""
    with open(RAIZ / "config" / "modelo.json", encoding="utf-8") as archivo:
        return json.load(archivo)

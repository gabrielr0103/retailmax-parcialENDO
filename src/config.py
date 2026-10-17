"""Carga la configuración del entorno activo (dev, qa o prod)."""

import json
import os
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent


def cargar_config(entorno: str | None = None) -> dict:
    """Lee config/<entorno>.yaml. Si no se indica, usa RETAILMAX_ENTORNO o dev."""
    entorno = entorno or os.getenv("RETAILMAX_ENTORNO", "dev")
    ruta = RAIZ / "config" / f"{entorno}.yaml"
    with open(ruta, encoding="utf-8") as archivo:
        return yaml.safe_load(archivo)


def cargar_config_modelo() -> dict:
    """Lee los hiperparámetros del modelo desde config/modelo.json."""
    with open(RAIZ / "config" / "modelo.json", encoding="utf-8") as archivo:
        return json.load(archivo)

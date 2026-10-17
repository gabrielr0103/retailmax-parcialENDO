"""Lectura de las ventas semanales."""

from pathlib import Path

import pandas as pd

COLUMNAS = ["semana", "pais", "tienda_id", "categoria", "unidades_vendidas", "precio_unitario"]


def leer_ventas(ruta: str | Path) -> pd.DataFrame:
    """Lee el CSV de ventas y convierte la columna semana a fecha."""
    df = pd.read_csv(ruta)
    df["semana"] = pd.to_datetime(df["semana"], errors="coerce")
    return df

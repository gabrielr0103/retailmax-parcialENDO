"""Pruebas de esquema y calidad sobre las ventas semanales.

Se ejecuta como paso del pipeline: si alguna regla falla, termina con código 1
y el pipeline se detiene antes de entrenar.
"""

import sys

import pandas as pd

from src.config import RAIZ, cargar_config
from src.extraer import COLUMNAS, leer_ventas

TIPOS_NUMERICOS = ["unidades_vendidas", "precio_unitario"]


def validar(df: pd.DataFrame, reglas: dict) -> list[str]:
    """Devuelve la lista de reglas que no se cumplen. Vacía si todo está bien."""
    errores = []

    faltantes = [c for c in COLUMNAS if c not in df.columns]
    if faltantes:
        return [f"Esquema: faltan las columnas {faltantes}"]

    for columna in TIPOS_NUMERICOS:
        if not pd.api.types.is_numeric_dtype(df[columna]):
            errores.append(f"Esquema: {columna} debe ser numérica")

    for columna in COLUMNAS:
        proporcion = df[columna].isna().mean()
        if proporcion > reglas["max_nulos"]:
            errores.append(
                f"Calidad: {columna} tiene {proporcion:.1%} de nulos "
                f"(máximo {reglas['max_nulos']:.0%})"
            )

    if errores:
        return errores

    if (df["unidades_vendidas"].dropna() < 0).any():
        errores.append("Calidad: hay unidades_vendidas negativas")
    if (df["precio_unitario"].dropna() <= 0).any():
        errores.append("Calidad: hay precio_unitario menor o igual a 0")

    paises = set(df["pais"].dropna()) - set(reglas["paises_validos"])
    if paises:
        errores.append(f"Calidad: países no reconocidos {sorted(paises)}")

    categorias = set(df["categoria"].dropna()) - set(reglas["categorias_validas"])
    if categorias:
        errores.append(f"Calidad: categorías no reconocidas {sorted(categorias)}")

    duplicados = df.duplicated(subset=["semana", "tienda_id", "categoria"]).sum()
    if duplicados:
        errores.append(f"Calidad: {duplicados} filas duplicadas por semana, tienda y categoría")

    return errores


def main() -> int:
    config = cargar_config()
    ruta = RAIZ / config["datos"]["ruta_ventas"]
    df = leer_ventas(ruta)
    errores = validar(df, config["calidad"])

    print(f"Validando {len(df)} filas de {config['datos']['ruta_ventas']} ({config['entorno']})")
    if errores:
        for error in errores:
            print(f"  FALLA  {error}")
        print("Resultado: los datos NO pasan las pruebas. Pipeline detenido.")
        return 1
    print("Resultado: esquema y calidad OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Construcción de variables para el modelo de predicción de ventas."""

import pandas as pd

LLAVE = ["tienda_id", "categoria"]


def construir_features(df: pd.DataFrame, rezagos: list[int], ventana: int) -> pd.DataFrame:
    """Agrega rezagos y media móvil por tienda y categoría.

    Todas las variables usan solo semanas anteriores (shift), así el modelo
    nunca ve la venta que tiene que predecir.
    """
    df = df.sort_values(LLAVE + ["semana"]).copy()
    grupo = df.groupby(LLAVE)["unidades_vendidas"]

    for rezago in rezagos:
        df[f"rezago_{rezago}"] = grupo.shift(rezago)
    df[f"media_movil_{ventana}"] = grupo.transform(lambda s: s.shift(1).rolling(ventana).mean())
    df["semana_del_anio"] = df["semana"].dt.isocalendar().week.astype(int)

    df = pd.get_dummies(df, columns=["pais", "categoria"], dtype=int)
    return df.dropna().reset_index(drop=True)


def columnas_modelo(df: pd.DataFrame) -> list[str]:
    """Columnas que entran al modelo: todo menos llaves, fecha y objetivo."""
    excluir = {"semana", "tienda_id", "unidades_vendidas", "precio_unitario"}
    return [c for c in df.columns if c not in excluir]

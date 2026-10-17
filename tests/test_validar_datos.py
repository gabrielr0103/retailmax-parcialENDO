import numpy as np
import pandas as pd

from src.config import RAIZ, cargar_config
from src.extraer import leer_ventas
from src.validar_datos import validar

REGLAS = cargar_config("dev")["calidad"]


def muestra():
    return leer_ventas(RAIZ / "data" / "muestra" / "ventas_muestra.csv")


def test_muestra_pasa_todas_las_reglas():
    assert validar(muestra(), REGLAS) == []


def test_falta_una_columna():
    df = muestra().drop(columns=["precio_unitario"])
    assert "faltan las columnas" in validar(df, REGLAS)[0]


def test_mas_de_10_por_ciento_de_nulos_en_precio_unitario():
    df = muestra()
    df.loc[df.sample(frac=0.12, random_state=1).index, "precio_unitario"] = np.nan
    errores = validar(df, REGLAS)
    assert any("precio_unitario tiene 12.0% de nulos" in e for e in errores)


def test_unidades_negativas():
    df = muestra()
    df.loc[0, "unidades_vendidas"] = -5
    assert any("negativas" in e for e in validar(df, REGLAS))


def test_filas_duplicadas():
    df = muestra()
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    assert any("duplicadas" in e for e in validar(df, REGLAS))


def test_pais_fuera_de_los_cinco():
    df = muestra()
    df.loc[0, "pais"] = "BR"
    assert any("BR" in e for e in validar(df, REGLAS))

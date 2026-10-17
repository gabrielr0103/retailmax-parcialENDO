import pandas as pd

from src.features import construir_features


def serie_simple():
    semanas = pd.date_range("2026-01-05", periods=8, freq="W-MON")
    return pd.DataFrame(
        {
            "semana": semanas,
            "pais": "CO",
            "tienda_id": "CO-T01",
            "categoria": "hogar",
            "unidades_vendidas": [10, 20, 30, 40, 50, 60, 70, 80],
            "precio_unitario": 45.0,
        }
    )


def test_rezagos_usan_solo_semanas_anteriores():
    df = construir_features(serie_simple(), rezagos=[1, 2], ventana=2)
    fila = df.iloc[0]
    assert fila["unidades_vendidas"] == 30
    assert fila["rezago_1"] == 20
    assert fila["rezago_2"] == 10
    assert fila["media_movil_2"] == 15


def test_no_quedan_nulos():
    df = construir_features(serie_simple(), rezagos=[1, 4], ventana=4)
    assert not df.isna().any().any()
    assert len(df) == 4

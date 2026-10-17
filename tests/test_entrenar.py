from src.config import RAIZ, cargar_config, cargar_config_modelo
from src.entrenar import entrenar, mape
from src.extraer import leer_ventas


def test_mape():
    assert mape([100, 200], [110, 180]) == 0.1


def test_modelo_mejora_la_linea_base_en_la_muestra():
    df = leer_ventas(RAIZ / "data" / "muestra" / "ventas_muestra.csv")
    _, metricas = entrenar(df, cargar_config("dev"), cargar_config_modelo())
    assert metricas["aprobado"]
    assert metricas["mape_modelo"] < metricas["mape_linea_base"]

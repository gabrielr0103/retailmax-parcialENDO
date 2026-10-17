"""Entrena el modelo de predicción de ventas y lo compara contra una línea base.

El modelo solo se acepta si su MAPE en las últimas semanas está por debajo del
umbral del entorno y si mejora a la predicción ingenua (repetir la semana anterior).
"""

import json
import sys
from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import Ridge

from src.config import RAIZ, cargar_config, cargar_config_modelo
from src.extraer import leer_ventas
from src.features import columnas_modelo, construir_features

CARPETA_ARTEFACTOS = RAIZ / "artefactos"


def mape(real, prediccion) -> float:
    real = np.asarray(real, dtype=float)
    prediccion = np.asarray(prediccion, dtype=float)
    return float(np.mean(np.abs((real - prediccion) / real)))


def entrenar(df, config: dict, config_modelo: dict) -> tuple[object, dict]:
    datos = construir_features(df, config_modelo["rezagos"], config_modelo["ventana_media_movil"])
    semanas = sorted(datos["semana"].unique())
    corte = semanas[-config["modelo"]["semanas_validacion"]]
    entreno = datos[datos["semana"] < corte]
    prueba = datos[datos["semana"] >= corte]

    columnas = columnas_modelo(datos)
    modelo = Ridge(**config_modelo["hiperparametros"])
    modelo.fit(entreno[columnas], entreno["unidades_vendidas"])

    metricas = {
        "mape_modelo": mape(prueba["unidades_vendidas"], modelo.predict(prueba[columnas])),
        "mape_linea_base": mape(prueba["unidades_vendidas"], prueba["rezago_1"]),
        "mape_maximo": config["modelo"]["mape_maximo"],
        "filas_entreno": int(len(entreno)),
        "filas_prueba": int(len(prueba)),
        "columnas": columnas,
    }
    metricas["aprobado"] = bool(
        metricas["mape_modelo"] <= metricas["mape_maximo"]
        and metricas["mape_modelo"] < metricas["mape_linea_base"]
    )
    return modelo, metricas


def main() -> int:
    config = cargar_config()
    df = leer_ventas(RAIZ / config["datos"]["ruta_ventas"])
    modelo, metricas = entrenar(df, config, cargar_config_modelo())

    CARPETA_ARTEFACTOS.mkdir(exist_ok=True)
    joblib.dump(modelo, CARPETA_ARTEFACTOS / "modelo_ventas.joblib")
    Path(CARPETA_ARTEFACTOS / "metricas.json").write_text(
        json.dumps(metricas, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"MAPE del modelo:     {metricas['mape_modelo']:.2%}")
    print(f"MAPE línea base:     {metricas['mape_linea_base']:.2%}")
    print(f"MAPE máximo ({config['entorno']}): {metricas['mape_maximo']:.0%}")
    if not metricas["aprobado"]:
        print("Resultado: el modelo NO cumple los criterios. No se empaqueta.")
        return 1
    print("Resultado: modelo aprobado")
    return 0


if __name__ == "__main__":
    sys.exit(main())

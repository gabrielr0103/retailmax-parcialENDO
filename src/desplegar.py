"""Despliegue del paquete del modelo en staging (qa) o producción (prod).

En el taller no hay credenciales de AWS, así que la copia a S3 se muestra como el
comando que se correría. Todo lo demás sí se ejecuta: revisar el hash del paquete,
cargar el modelo y hacer una prueba de humo con predicciones reales sobre la muestra.
"""

import argparse
import json
import sys
import tarfile
import tempfile
from pathlib import Path

import joblib
import numpy as np

from src.config import RAIZ, cargar_config
from src.empaquetar import sha256_archivo
from src.extraer import leer_ventas
from src.features import construir_features

MUESTRA = RAIZ / "data" / "muestra" / "ventas_muestra.csv"


def verificar_y_probar(paquete: Path) -> dict:
    """Revisa el hash, carga el modelo y predice la última semana de la muestra."""
    esperado = Path(f"{paquete}.sha256").read_text().split()[0]
    if sha256_archivo(paquete) != esperado:
        raise ValueError("El hash del paquete no coincide: se modificó después de empaquetarlo.")

    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(paquete) as tar:
            tar.extractall(tmp, filter="data")
        manifiesto = json.loads((Path(tmp) / "manifiesto.json").read_text(encoding="utf-8"))
        modelo = joblib.load(Path(tmp) / "modelo_ventas.joblib")

    config_modelo = manifiesto["config_modelo"]
    datos = construir_features(
        leer_ventas(MUESTRA), config_modelo["rezagos"], config_modelo["ventana_media_movil"]
    )
    ultima_semana = datos[datos["semana"] == datos["semana"].max()]
    prediccion = modelo.predict(ultima_semana[manifiesto["columnas"]])
    if not (np.isfinite(prediccion).all() and (prediccion > 0).all()):
        raise ValueError("La prueba de humo dio predicciones vacías o negativas.")
    return manifiesto


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entorno", choices=["qa", "prod"], required=True)
    parser.add_argument("--paquete", required=True, type=Path)
    args = parser.parse_args(argv)

    nombre = "staging" if args.entorno == "qa" else "producción"
    try:
        manifiesto = verificar_y_probar(args.paquete)
    except (ValueError, FileNotFoundError) as error:
        print(f"Despliegue en {nombre} detenido: {error}")
        return 1

    bucket = cargar_config(args.entorno)["datos"]["bucket"]
    print(f"Paquete {args.paquete.name} verificado (commit {manifiesto['commit']})")
    print(f"MAPE del modelo: {manifiesto['metricas']['mape_modelo']:.2%}")
    print("Prueba de humo: predicciones de la última semana OK")
    print(f"[simulado] aws s3 cp {args.paquete} s3://{bucket}/modelos/{args.paquete.name}")
    print(f"Despliegue en {nombre}: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

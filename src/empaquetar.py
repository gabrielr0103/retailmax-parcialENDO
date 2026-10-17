"""Empaqueta el modelo aprobado junto con lo necesario para saber de dónde salió.

El paquete lleva el modelo, sus métricas y un manifiesto con la versión, el commit,
el hash de los datos de entrenamiento y los hiperparámetros. Al lado queda un .sha256
que el despliegue revisa antes de usar el paquete.
"""

import hashlib
import json
import os
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from src.config import RAIZ, cargar_config, cargar_config_modelo
from src.entrenar import CARPETA_ARTEFACTOS

CARPETA_DIST = RAIZ / "dist"


def md5_archivo(ruta: Path) -> str:
    return hashlib.md5(Path(ruta).read_bytes()).hexdigest()


def sha256_archivo(ruta: Path) -> str:
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def empaquetar(
    version: str, commit: str, artefactos: Path, ruta_datos: Path, destino: Path
) -> Path:
    """Crea destino/modelo_ventas-<version>.tar.gz y su archivo .sha256."""
    metricas = json.loads((artefactos / "metricas.json").read_text(encoding="utf-8"))
    if not metricas["aprobado"]:
        raise ValueError("El modelo no fue aprobado en Train & Validate; no se empaqueta.")

    manifiesto = {
        "modelo": "prediccion_ventas",
        "version": version,
        "commit": commit,
        "creado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "datos_entrenamiento": {
            "ruta": str(Path(ruta_datos).relative_to(RAIZ)),
            "md5": md5_archivo(ruta_datos),
        },
        "config_modelo": cargar_config_modelo(),
        "metricas": {
            "mape_modelo": metricas["mape_modelo"],
            "mape_linea_base": metricas["mape_linea_base"],
            "mape_maximo": metricas["mape_maximo"],
        },
        "columnas": metricas["columnas"],
    }

    destino.mkdir(parents=True, exist_ok=True)
    paquete = destino / f"modelo_ventas-{version}.tar.gz"
    with tempfile.TemporaryDirectory() as tmp:
        ruta_manifiesto = Path(tmp) / "manifiesto.json"
        ruta_manifiesto.write_text(
            json.dumps(manifiesto, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        with tarfile.open(paquete, "w:gz") as tar:
            tar.add(artefactos / "modelo_ventas.joblib", arcname="modelo_ventas.joblib")
            tar.add(artefactos / "metricas.json", arcname="metricas.json")
            tar.add(ruta_manifiesto, arcname="manifiesto.json")

    Path(f"{paquete}.sha256").write_text(f"{sha256_archivo(paquete)}  {paquete.name}\n")
    return paquete


def main() -> None:
    config = cargar_config()
    version = os.getenv("VERSION_MODELO", "0.0.0-local")
    commit = os.getenv("GITHUB_SHA", os.getenv("GIT_COMMIT", "local"))[:7]
    paquete = empaquetar(
        version,
        commit,
        CARPETA_ARTEFACTOS,
        RAIZ / config["datos"]["ruta_ventas"],
        CARPETA_DIST,
    )
    print(f"Paquete creado: {paquete.relative_to(RAIZ)}")
    print(f"SHA-256: {sha256_archivo(paquete)}")


if __name__ == "__main__":
    main()

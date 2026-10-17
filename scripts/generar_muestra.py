"""Genera data/muestra/ventas_muestra.csv, la muestra sintética que usan las pruebas y el CI.

La semilla es fija, así que correrlo de nuevo produce exactamente el mismo archivo.
La ficha data/procedencia/ventas_muestra.yaml guarda su hash para comprobarlo.
"""

import csv
import datetime
import math
import random

from src.config import RAIZ

SEMILLA = 42
PAISES = {"CO": 1.0, "MX": 1.4, "PE": 0.7, "CL": 0.9, "AR": 0.8}
CATEGORIAS = {"tecnologia": (60, 310.0), "hogar": (110, 46.0), "moda": (150, 24.5)}
INICIO = datetime.date(2026, 1, 5)
SEMANAS = 30


def generar() -> list[list]:
    random.seed(SEMILLA)
    filas = []
    for pais, factor in PAISES.items():
        for tienda in (1, 2):
            for categoria, (base, precio) in CATEGORIAS.items():
                nivel = base * factor * (1.15 if tienda == 1 else 0.85)
                for w in range(SEMANAS):
                    semana = INICIO + datetime.timedelta(weeks=w)
                    estacionalidad = 1 + 0.18 * math.sin(2 * math.pi * w / 13)
                    tendencia = 1 + 0.006 * w
                    ruido = random.gauss(1, 0.06)
                    unidades = max(1, round(nivel * estacionalidad * tendencia * ruido))
                    precio_semana = round(precio * random.uniform(0.97, 1.03), 2)
                    filas.append(
                        [
                            semana.isoformat(),
                            pais,
                            f"{pais}-T0{tienda}",
                            categoria,
                            unidades,
                            f"{precio_semana:.2f}",
                        ]
                    )
    return filas


def main() -> None:
    ruta = RAIZ / "data" / "muestra" / "ventas_muestra.csv"
    with open(ruta, "w", newline="") as archivo:
        escritor = csv.writer(archivo, lineterminator="\n")
        escritor.writerow(
            ["semana", "pais", "tienda_id", "categoria", "unidades_vendidas", "precio_unitario"]
        )
        escritor.writerows(generar())
    print(f"Muestra generada en {ruta.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()

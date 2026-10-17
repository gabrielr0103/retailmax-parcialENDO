# RetailMax Analytics: DataOps del modelo de predicción de ventas

Taller práctico de ENDO (DataOps), segundo corte.
Gabriel Rodríguez · Profesora María José Torres Nieves · Escuela Colombiana de Ingeniería

RetailMax vende en tiendas físicas y por e-commerce en Colombia, México, Perú, Chile y Argentina. En este repositorio está lo necesario para reconstruir el modelo que predice las unidades vendidas por semana, tienda y categoría: el código, la configuración de cada entorno, los pipelines, la infraestructura en Terraform y el registro de qué datos se usaron para entrenar cada versión.

## Estructura

```
retailmax-dataops/
├── src/                      código del pipeline (extraer, validar, features, entrenar)
├── notebooks/                notebooks exportados a .py con jupytext
├── sql/                      consulta de extracción
│   └── migraciones/          cambios de esquema numerados (V001, V002) y su reversa (U002)
├── config/                   dev.yaml, qa.yaml, prod.yaml y modelo.json
├── mdm/                      definición maestra de cliente activo
├── pipelines/
│   ├── airflow/dags/         DAG semanal de reentrenamiento
│   └── jenkins/Jenkinsfile   el mismo CI para quien use Jenkins
├── infra/terraform/          infraestructura como código
├── data/
│   ├── raw/                  solo el puntero .dvc; el CSV vive en el remoto de DVC
│   ├── muestra/              muestra sintética para pruebas y CI
│   └── procedencia/          una ficha YAML por dataset
├── scripts/                  generador de la muestra
├── tests/                    pruebas unitarias y de datos
├── .github/                  CI, plantilla de PR y CODEOWNERS
├── dvc.yaml                  etapas validar y entrenar para dvc repro
└── evidencias/               capturas del taller
```

## Qué se versiona en Git

| Qué | Dónde | Por qué |
|---|---|---|
| Código Python | `src/`, `scripts/` | Es lo que más cambia y lo que se revisa en cada PR. |
| Notebooks exportados | `notebooks/*.py` | En el diff de un .py se ve qué celda cambió. Un .ipynb mezcla código con salidas e imágenes y casi no se puede revisar. |
| SQL y migraciones | `sql/` | La consulta de extracción define qué entra al modelo. Las migraciones numeradas se aplican o se revierten en el mismo orden en todos los entornos. |
| Configuración | `config/`, `mdm/` | Dev, QA y PROD corren el mismo código y solo cambian estos archivos. Los umbrales del modelo y la regla de cliente activo también se aprueban por PR. |
| Pipelines | `pipelines/`, `.github/workflows/`, `dvc.yaml` | Si el pipeline vive fuera del repo, nadie sabe qué versión corrió en producción. |
| Terraform | `infra/terraform/` | Los entornos se crean desde el código y cualquier cambio pasa por revisión. |
| Punteros de datos y fichas de procedencia | `data/raw/*.dvc`, `data/procedencia/` | Pesan unos pocos bytes y amarran cada commit a una versión exacta de los datos. |
| Muestra sintética | `data/muestra/` | Pesa 34 KB y no tiene datos reales, así que el CI corre las pruebas sin credenciales. |

## Qué no se versiona y por qué

| Qué | Por qué | Dónde queda |
|---|---|---|
| Datos crudos (`data/raw/*.csv`) | Pesan, cambian cada semana y Git guardaría una copia completa por versión. | Remoto de DVC en S3. |
| Modelos entrenados (`*.joblib`, `*.pkl`) y métricas | Se regeneran con el código y los datos de un commit. Son binarios, así que el diff no dice nada. | Registro de artefactos, en la etapa de empaquetado. |
| Archivos `.ipynb` | Las salidas guardan pedazos de datos y generan conflictos cada vez que alguien corre el notebook. | En el equipo de quien trabaja. En Git va el .py. |
| Credenciales (`.env`, llaves, `.aws/`) | Cualquiera con acceso al repo tendría acceso a las bases y a AWS. | Secretos de GitHub Actions, Jenkins o AWS Secrets Manager. |
| Estado de Terraform (`*.tfstate`) | Guarda IDs de recursos y a veces contraseñas en texto plano. Dos copias locales distintas terminan dañando el entorno. | Backend remoto en S3 con bloqueo. |
| `.venv/`, `.terraform/`, cachés | Se reconstruyen con `pip install` y `terraform init`. | En cada máquina. |

## Procedencia de los datos

Cada dataset de entrenamiento queda registrado en tres archivos que cambian juntos, en el mismo commit:

1. `data/raw/ventas_semanales.csv.dvc` tiene el hash md5 y el tamaño del CSV. DVC usa ese hash para traer el archivo exacto desde el remoto.
2. `data/procedencia/ventas_semanales.yaml` dice de qué sistemas salió, con qué consulta y parámetros, qué transformaciones tuvo y quién es el data owner. También lleva el historial de versiones con sus hashes.
3. `sql/ventas_semanales.sql` es la consulta que produjo el archivo.

Con eso se puede saber qué datos entrenaron un modelo. Si la versión v1.0.0 empieza a fallar, se vuelve a ese punto así:

```bash
git checkout v1.0.0
dvc pull
```

El código, la configuración y el CSV quedan como estaban ese día, y la ficha dice de dónde salió cada fila. Un PR que cambie los datos sin actualizar la ficha no pasa la revisión, porque está en la lista de la plantilla.

La muestra de `data/muestra/` tiene su propia ficha. Se regenera con `python -m scripts.generar_muestra` y su hash queda anotado para comprobar que salió igual.

En este taller el remoto `s3://retailmax-dvc-almacen` es simulado. No hay credenciales de AWS, entonces `dvc pull` no descarga nada y las pruebas y el CI usan la muestra.

## Flujo de ramas

- `main` tiene lo que está en producción. Solo recibe PRs desde `develop` y cada fusión lleva un tag de versión.
- `develop` es la rama de integración y recibe PRs desde las ramas `feature/*`.
- Cada cambio va en su propia rama `feature/*`. El PR hacia `develop` necesita los tres checks del CI en verde y una revisión.

## Cómo correrlo

Con Python 3.12:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ruff check .
pytest -q
python -m src.validar_datos
python -m src.entrenar
```

Por defecto usa `config/dev.yaml` y la muestra. Para otro entorno: `RETAILMAX_ENTORNO=qa python -m src.entrenar`.

## Ejercicios del taller

| Ejercicio | Dónde está |
|---|---|
| 8. Estructura del repositorio | El árbol de arriba |
| 9. README de versionamiento | Este archivo |
| 10. Commit, PR y revisión | Historial de commits, PR hacia `develop` y carpeta `.github/` |

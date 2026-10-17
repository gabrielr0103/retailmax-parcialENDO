"""DAG semanal del modelo de predicción de ventas.

Corre los lunes a las 6:00. Trae la versión de datos registrada en DVC, valida
esquema y calidad, entrena y publica las métricas. Si la validación falla, las
tareas siguientes no corren.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

REPO = "/opt/airflow/repos/retailmax-dataops"
ENTORNO = {"RETAILMAX_ENTORNO": "{{ var.value.get('retailmax_entorno', 'qa') }}"}

ARGUMENTOS = {
    "owner": "equipo-datos",
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="modelo_ventas_semanal",
    description="Trae, valida y entrena el modelo de predicción de ventas",
    schedule="0 6 * * 1",
    start_date=datetime(2026, 10, 19),
    catchup=False,
    default_args=ARGUMENTOS,
    tags=["retailmax", "ventas", "modelo"],
) as dag:
    traer_datos = BashOperator(
        task_id="traer_datos_dvc",
        bash_command=f"cd {REPO} && git pull && dvc pull data/raw/ventas_semanales.csv.dvc",
    )

    validar_datos = BashOperator(
        task_id="validar_datos",
        bash_command=f"cd {REPO} && python -m src.validar_datos",
        env=ENTORNO,
        append_env=True,
    )

    entrenar = BashOperator(
        task_id="entrenar_modelo",
        bash_command=f"cd {REPO} && python -m src.entrenar",
        env=ENTORNO,
        append_env=True,
    )

    publicar_metricas = BashOperator(
        task_id="publicar_metricas",
        bash_command=f"cd {REPO} && cat artefactos/metricas.json",
    )

    traer_datos >> validar_datos >> entrenar >> publicar_metricas

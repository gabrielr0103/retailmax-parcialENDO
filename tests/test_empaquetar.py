import json

import joblib
import pytest

from src.config import RAIZ, cargar_config, cargar_config_modelo
from src.desplegar import verificar_y_probar
from src.empaquetar import empaquetar
from src.entrenar import entrenar
from src.extraer import leer_ventas

MUESTRA = RAIZ / "data" / "muestra" / "ventas_muestra.csv"


@pytest.fixture
def paquete(tmp_path):
    modelo, metricas = entrenar(leer_ventas(MUESTRA), cargar_config("prod"), cargar_config_modelo())
    artefactos = tmp_path / "artefactos"
    artefactos.mkdir()
    joblib.dump(modelo, artefactos / "modelo_ventas.joblib")
    (artefactos / "metricas.json").write_text(json.dumps(metricas))
    return empaquetar("1.0.0", "abc1234", artefactos, MUESTRA, tmp_path / "dist")


def test_paquete_pasa_la_prueba_de_humo(paquete):
    manifiesto = verificar_y_probar(paquete)
    assert manifiesto["version"] == "1.0.0"
    assert manifiesto["datos_entrenamiento"]["md5"] == "a84b15a27182ab634cf854f6dffe4ca3"


def test_paquete_modificado_no_se_despliega(paquete):
    with open(paquete, "ab") as archivo:
        archivo.write(b"cambio")
    with pytest.raises(ValueError, match="hash"):
        verificar_y_probar(paquete)

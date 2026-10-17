# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Exploración de ventas semanales
#
# Primera mirada a la muestra antes de definir las variables del modelo.
# Este archivo es la exportación del notebook con jupytext: en Git queda el
# código de cada celda, sin salidas ni imágenes, y los cambios se pueden revisar en un PR.

# %%
from src.config import RAIZ
from src.extraer import leer_ventas

df = leer_ventas(RAIZ / "data" / "muestra" / "ventas_muestra.csv")
df.info()

# %% [markdown]
# Unidades totales por país y categoría.

# %%
df.pivot_table(index="pais", columns="categoria", values="unidades_vendidas", aggfunc="sum")

# %% [markdown]
# Serie semanal de una tienda. La curva sube y baja cada 13 semanas más o menos,
# por eso el modelo usa rezagos y una media móvil de 4 semanas.

# %%
tienda = df[(df["tienda_id"] == "CO-T01") & (df["categoria"] == "hogar")]
tienda.set_index("semana")["unidades_vendidas"].plot(title="CO-T01, hogar")

# %% [markdown]
# Correlación de las ventas con la semana anterior y con la de hace cuatro semanas.

# %%
serie = tienda["unidades_vendidas"].reset_index(drop=True)
print("rezago 1:", round(serie.autocorr(1), 2))
print("rezago 4:", round(serie.autocorr(4), 2))

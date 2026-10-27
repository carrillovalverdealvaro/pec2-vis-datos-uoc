import polars as pl
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

root_path = Path(os.getenv("ROOT_PATH"))


def procesar_generacion_energia_treemap():
    file_generacion_raw = (
        root_path / "data" / "raw" / "estructura_generacion_electrica.xlsx"
    )

    folder_generacion_procesado = root_path / "data" / "interim"
    folder_generacion_procesado.mkdir(exist_ok=True)

    df_generacion_raw = pl.read_excel(file_generacion_raw)

    # Eliminar los "-" de los datos

    df_generacion_raw = df_generacion_raw.with_columns(pl.col("*").replace("-", "0"))

    # Vamos a transformar las variables str a Float para poder sumarlas

    columns_to_cast = df_generacion_raw.columns[1:]

    cast = {}

    for column in columns_to_cast:
        cast[column] = pl.Float64

    df_generacion_raw = df_generacion_raw.cast(cast)

    # Se suman las columnas para obtener la generación total por energía

    df_generacion_raw = df_generacion_raw.with_columns(
        pl.sum_horizontal(*columns_to_cast).round(2).alias("Generación total")
    )

    gwh_generados_totales = df_generacion_raw.filter(
        pl.col("Tipo energía") == "Generación total"
    ).item(0, "Generación total")

    df_generacion = (
        df_generacion_raw.select("Tipo energía", "Generación total")
        .with_columns(
            (pl.col("Generación total") / gwh_generados_totales * 100)
            .round(2)
            .alias("Porcentaje Generación")
        )
        .filter(pl.col("Tipo energía") != "Generación total")
    )

    # Se crea la clasificación por tipo de energía
    CLASIFICACION = {
        "Hidráulica": "Renovable",
        "Hidroeólica": "Renovable",
        "Eólica": "Renovable",
        "Solar fotovoltaica": "Renovable",
        "Solar térmica": "Renovable",
        "Otras renovables": "Renovable",
        "Residuos renovables": "Renovable",
        "Turbinación bombeo": "No renovable",
        "Nuclear": "No renovable",
        "Carbón": "No renovable",
        "Fuel + Gas": "No renovable",
        "Motores diésel": "No renovable",
        "Turbina de gas": "No renovable",
        "Turbina de vapor": "No renovable",
        "Ciclo combinado": "No renovable",
        "Cogeneración": "No renovable",
        "Residuos no renovables": "No renovable",
    }

    df_generacion = df_generacion.with_columns(
        pl.col("Tipo energía")
        .replace_strict(CLASIFICACION, default=None)
        .alias("Es renovable")
    )

    df_generacion.write_parquet(
        folder_generacion_procesado / "estructura_generacion_electrica_treemap.parquet"
    )


def procesar_generacion_energia_nightingale_chart():
    file_generacion_raw = (
        root_path / "data" / "raw" / "estructura_generacion_electrica.xlsx"
    )

    folder_generacion_procesado = root_path / "data" / "interim"
    folder_generacion_procesado.mkdir(exist_ok=True)

    df_generacion_raw = pl.read_excel(file_generacion_raw)

    # Eliminar los "-" de los datos

    df_generacion_raw = df_generacion_raw.with_columns(pl.col("*").replace("-", "0"))

    # Vamos a transformar las variables str a Float para poder sumarlas

    columns_to_cast = df_generacion_raw.columns[1:]

    cast = {}

    for column in columns_to_cast:
        cast[column] = pl.Float64

    df_generacion_raw = df_generacion_raw.cast(cast)

    # Se suman las columnas para obtener la generación total por energía
    meses = df_generacion_raw.columns[1:]

    meses_df = pl.DataFrame({"Mes": meses}).with_columns(
        pl.arange(1, len(meses) + 1).alias("Número de mes")
    )

    df_mes= (
        df_generacion_raw.unpivot(
            index="Tipo energía", variable_name="Mes", value_name="Generación"
        )
        .join(meses_df, on="Mes", how="inner")
        .filter(pl.col("Tipo energía") != "Generación total")
        .sort("Número de mes", "Tipo energía")
    )

    

    # Se crea la clasificación por tipo de energía
    CLASIFICACION = {
        "Hidráulica": "Renovable",
        "Hidroeólica": "Renovable",
        "Eólica": "Renovable",
        "Solar fotovoltaica": "Renovable",
        "Solar térmica": "Renovable",
        "Otras renovables": "Renovable",
        "Residuos renovables": "Renovable",
        "Turbinación bombeo": "No renovable",
        "Nuclear": "Nuclear",
        "Carbón": "No renovable",
        "Fuel + Gas": "No renovable",
        "Motores diésel": "No renovable",
        "Turbina de gas": "No renovable",
        "Turbina de vapor": "No renovable",
        "Ciclo combinado": "No renovable",
        "Cogeneración": "No renovable",
        "Residuos no renovables": "No renovable",
    }

    df_mes = df_mes.with_columns(
        pl.col("Tipo energía")
        .replace_strict(CLASIFICACION, default=None)
        .alias("Es renovable")
    )

    df_mes.write_parquet(
        folder_generacion_procesado
        / "estructura_generacion_electrica_nightingale_chart.parquet"
    )

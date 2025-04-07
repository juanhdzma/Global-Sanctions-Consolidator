from pandas import read_excel, Series
from src.util.comparer import compare_names_matrix
from numpy import max, argmax
from src.util.excel_helper import save_to_excel
from src.util.error import CustomError
from src.util.data_helpers import leer_contador, guardar_contador, format_name
from datetime import datetime
from pandas import DataFrame

TRANSFER_PATH = "./Transfer.xlsx"


def load_and_transform_transfer_excel(file_path):
    """Carga el archivo en un DataFrame y realiza las transformaciones necesarias"""
    df = read_excel(file_path, dtype=str)
    df = df[["NOMBRE"]]
    return df


def compare_lists(df, transfer):
    """Compara listas y encuentra los mejores matches, agregando columnas de comparacion"""
    if df.empty:
        df["COMPARADO"] = Series(dtype=str)
        df["SCORE"] = Series(dtype=float)
        return df

    df_names_array = df["NOMBRE COMPLETO"].fillna("N/A").values
    transfer_names_array = transfer["NOMBRE"].values

    score_matrix = compare_names_matrix(df_names_array, transfer_names_array)

    best_match_indices = argmax(score_matrix, axis=1)
    best_scores = max(score_matrix, axis=1)

    df["COMPARADO"] = transfer_names_array[best_match_indices]
    df["SCORE"] = best_scores * 100

    return df


def transform_df(df, kind):
    new_rows = []

    contador = leer_contador()
    fecha_hoy = datetime.today().strftime("%d-%m-%Y")

    for _, row in df.iterrows():
        name = row["NOMBRE COMPLETO"]
        contador += 1
        new_rows.append(
            {
                "MOVIMI": "A",
                "TIPOID": "S",
                "NIT": contador,
                "NOMBRE": format_name(name),
                "TIPOCL": "C",
                "OBSERV": f"{kind} {fecha_hoy}",
                "NOMBRE COMPLETO": name,
            }
        )
    guardar_contador(contador)
    expanded_df = DataFrame(new_rows)
    return expanded_df


def generate_comparison_file_generic(file_name, pub_date, type):
    """Genera la comparación de nombres y documentos con el archivo Transfer"""

    try:
        df = read_excel(f"./output_files/{file_name}", dtype=str)
    except Exception:
        raise CustomError(f"Lectura del archivo: {file_name}")

    yield True  # Leer archivo

    try:
        transfer = load_and_transform_transfer_excel(TRANSFER_PATH)
        df = transform_df(df, type)
    except Exception as e:
        print(e)
        raise CustomError(f"Cargue del archivo de transferencias y transformación: {TRANSFER_PATH}")

    yield True  # Leer el transfer

    try:
        final = compare_lists(df, transfer)
    except Exception:
        raise CustomError("Comparación de los nombres.")

    yield True  # Comparar nombres

    try:
        filename = f"{type}_Transfer_{pub_date}.xlsx"
        save_to_excel(final, filename)
    except Exception:
        raise CustomError(f"Proceso de guardado el archivo final: {filename}")

    yield True  # Guardar Archivo Final

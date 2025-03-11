from pandas import read_excel, Series
from src.util.comparer import compare_names_matrix
from numpy import max, argmax
from src.util.excel_helper import save_to_excel
from src.util.error import CustomError

TRANSFER_PATH = "./Transfer.xlsx"


def load_and_transform_transfer_excel(file_path):
    """Carga el archivo en un DataFrame y realiza las transformaciones necesarias"""
    df = read_excel(file_path, dtype=str)
    df = df[["NOMBRE"]]
    return df


def compare_lists(df, transfer):
    """Compara listas y encuentra los mejores matches, agregando columnas de comparacion"""
    if df.empty:
        df["Comparado"] = Series(dtype=str)
        df["Score"] = Series(dtype=float)
        return df

    df_names_array = df["NOMBRE"].fillna("N/A").values
    transfer_names_array = transfer["NOMBRE"].values

    score_matrix = compare_names_matrix(df_names_array, transfer_names_array)

    best_match_indices = argmax(score_matrix, axis=1)
    best_scores = max(score_matrix, axis=1)

    df["Comparado"] = transfer_names_array[best_match_indices]
    df["Score"] = best_scores * 100

    return df


def generate_comparison_file_ue(file_name, pub_date):
    """Genera la comparación de nombres y documentos con el archivo Transfer"""

    try:
        df = read_excel(f"./output_files/{file_name}", dtype=str)
    except Exception:
        raise CustomError(f"❌ No se pudo leer el archivo: {file_name}")

    yield True  # Leer archivo

    try:
        transfer = load_and_transform_transfer_excel(TRANSFER_PATH)
    except Exception:
        raise CustomError(
            f"❌ No se pudo cargar el archivo de transferencias: {TRANSFER_PATH}"
        )

    yield True  # Leer el transfer

    try:
        final = compare_lists(df, transfer)
    except Exception:
        raise CustomError("❌ Error al comparar los nombres.")

    yield True  # Comparar nombres

    try:
        filename = f"UE_Transfer_{pub_date}.xlsx"
        save_to_excel(final, filename)
    except Exception:
        raise CustomError(f"❌ No se pudo guardar el archivo final: {filename}")

    yield True  # Guardar Archivo Final

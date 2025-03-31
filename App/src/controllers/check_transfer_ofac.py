from ast import literal_eval
from pandas import notna, DataFrame, read_excel
from src.util.data_helpers import verify_if_contain_number
from src.util.comparer import compare_names, compare_names_matrix
from numpy import max, argmax
from src.util.excel_helper import save_to_excel
from src.util.error import CustomError

TRANSFER_PATH = "./Transfer.xlsx"

MIN_ALIAS_LENGTH = 6
MIN_SCORE_ALIAS = 0.5


def process_aliases(df):
    """Procesa la columna Alias para convertir las cadenas en listas"""
    df["Alias"] = df["Alias"].apply(lambda x: literal_eval(x) if notna(x) else [])


def process_documents(df):
    """Procesa la columna Documentos para convertir las cadenas en listas"""
    df["Documentos"] = df["Documentos"].apply(
        lambda x: literal_eval(x) if notna(x) else []
    )


def filter_names(df):
    """Filtra los alias y los deja en la columna Alias con los nombres similares"""
    for idx, row in df.iterrows():
        full_name = row["Nombre Completo"]
        names = []
        for alias in row["Alias"]:
            if verify_if_contain_number(alias):
                continue
            if len(alias) < MIN_ALIAS_LENGTH:
                continue
            if "," in alias or "." in alias:
                names.append(alias)
            elif compare_names(full_name, alias) > MIN_SCORE_ALIAS:
                names.append(alias)
        df.at[idx, "Alias"] = names


def filter_documents(df):
    """Filtra los documentos y los deja en la columna Documentos con los documentos válidos"""
    for idx, row in df.iterrows():
        new_documents = [
            doc for doc in row["Documentos"] if doc.split()[0] in ["CC", "PAS", "NIT"]
        ]
        if not new_documents:
            new_documents.append(f"OFAC {row['ID OFAC']}")
        df.at[idx, "Documentos"] = new_documents


def expand_dataframe(df):
    """Expande el DataFrame original a uno nuevo con las combinaciones de nombres y documentos"""
    new_rows = []
    for _, row in df.iterrows():
        names = [row["Nombre Completo"]] + row["Alias"]
        documents = row["Documentos"]
        entity_id = row["ID OFAC"]

        for name in names:
            for document in documents:
                new_rows.append(
                    {
                        "ID OFAC": entity_id,
                        "NOMBRE": name,
                        "DOCUMENTO": document,
                        "Accion": row["Accion"],
                    }
                )

    expanded_df = DataFrame(new_rows)
    return expanded_df


def load_and_transform_transfer_excel(file_path):
    """Carga el archivo en un DataFrame y realiza las transformaciones necesarias"""
    df = read_excel(file_path, dtype=str)
    df = df[["NOMBRE", "ID OFAC"]]
    return df


def compare_lists(df, transfer):
    """Compara listas y encuentra los mejores matches, agregando columnas de comparacion"""
    mask_modify = df["Accion"] == "modify"
    df.loc[mask_modify, "ID OFAC Comparado"] = df.loc[mask_modify, "ID OFAC"]
    df.loc[mask_modify, "Comparado"] = df.loc[mask_modify, "NOMBRE"]
    df.loc[mask_modify, "Score"] = 100

    df_to_compare = df[~mask_modify]

    if not df_to_compare.empty:
        df_names_array = df_to_compare["NOMBRE"].fillna("N/A").values
        transfer_names_array = transfer["NOMBRE"].values
        transfer_id_array = transfer["ID OFAC"].values

        score_matrix = compare_names_matrix(df_names_array, transfer_names_array)

        best_match_indices = argmax(score_matrix, axis=1)
        best_scores = max(score_matrix, axis=1)

        df.loc[~mask_modify, "ID OFAC Comparado"] = transfer_id_array[
            best_match_indices
        ]
        df.loc[~mask_modify, "Comparado"] = transfer_names_array[best_match_indices]
        df.loc[~mask_modify, "Score"] = best_scores * 100

    return df


def generate_comparison_file_ofac(file_name, pub_date):
    """Genera la comparación de nombres y documentos con el archivo Transfer"""

    try:
        df = read_excel(f"./output_files/{file_name}", dtype=str)
    except Exception:
        raise CustomError(f"Lectura del archivo: {file_name}")

    yield True  # Leer archivo

    try:
        process_aliases(df)
        process_documents(df)
        filter_names(df)
        filter_documents(df)

    except Exception:
        raise CustomError("Procesamiento de nombres, alias y documentos.")

    yield True  # Procesar Nombres, Alias y Documentos

    try:
        df = expand_dataframe(df)
    except Exception:
        raise CustomError("Intentando expandir el DataFrame.")

    try:
        transfer = load_and_transform_transfer_excel(TRANSFER_PATH)
    except Exception:
        raise CustomError(
            f"❌ No se pudo cargar el archivo de transferencias: {TRANSFER_PATH}"
        )

    try:
        final = compare_lists(df, transfer)
    except Exception:
        raise CustomError("Comparación de los nombres.")

    yield True  # Comparar nombres

    try:
        filename = f"OFAC_Transfer_{pub_date}.xlsx"
        save_to_excel(final, filename)
    except Exception:
        raise CustomError(f"Proceso de guardado el archivo final: {filename}")

    yield True  # Guardar Archivo Final

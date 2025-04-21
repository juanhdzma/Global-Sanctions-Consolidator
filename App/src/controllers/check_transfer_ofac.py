from ast import literal_eval
from pandas import notna, DataFrame, read_excel
from src.util.comparer import compare_names, compare_names_matrix
from numpy import max, argmax
from src.util.excel_helper import save_to_excel
from src.util.error import CustomError
from src.util.data_helpers import leer_contador, guardar_contador, format_name
from datetime import datetime

TRANSFER_PATH = "./Transfer.xlsx"

MIN_ALIAS_LENGTH = 6
MIN_SCORE_ALIAS = 0.5


def process_aliases(df):
    """Procesa la columna Alias para convertir las cadenas en listas"""
    df["ALIAS"] = df["ALIAS"].apply(lambda x: literal_eval(x) if notna(x) else [])


def process_documents(df):
    """Procesa la columna Documentos para convertir las cadenas en listas"""
    df["DOCUMENTOS"] = df["DOCUMENTOS"].apply(lambda x: literal_eval(x) if notna(x) else [])


def filter_names(df):
    """Filtra los alias y los deja en la columna Alias con los nombres similares"""
    for idx, row in df.iterrows():
        full_name = row["NOMBRE COMPLETO"]
        names = []
        for alias in row["ALIAS"]:
            if len(alias) < MIN_ALIAS_LENGTH:
                continue
            if "," in alias or "." in alias:
                names.append(alias)
            elif compare_names(full_name, alias) > MIN_SCORE_ALIAS:
                names.append(alias)
        df.at[idx, "ALIAS"] = names


def filter_documents(df):
    """Filtra los documentos y los deja en la columna Documentos con los documentos válidos"""
    for idx, row in df.iterrows():
        new_documents = [doc for doc in row["DOCUMENTOS"] if doc.split()[0] in ["C", "P", "N"]]
        if not new_documents:
            new_documents.append(f"S {row['ID OFAC']}")
        df.at[idx, "DOCUMENTOS"] = new_documents


def expand_dataframe(df):
    """Expande el DataFrame original a uno nuevo con las combinaciones de nombres y documentos"""
    new_rows = []

    contador = leer_contador()
    fecha_hoy = datetime.today().strftime("%d-%m-%Y")

    for _, row in df.iterrows():
        names = [row["NOMBRE COMPLETO"]] + row["ALIAS"]
        documents = row["DOCUMENTOS"]
        entity_id = row["ID OFAC"]

        for name in names:
            for document in documents:
                if document.split()[0] == "S":
                    contador += 1
                    nit = contador
                else:
                    nit = document.split()[1]
                new_rows.append(
                    {
                        "MOVIMI": "A",
                        "TIPOID": document.split()[0],
                        "NIT": nit,
                        "NOMBRE": format_name(name),
                        "TIPOCL": "C",
                        "OBSERV": f"OFAC {fecha_hoy}",
                        "ID OFAC": entity_id,
                        "NOMBRE COMPLETO": name,
                        "DOCUMENTO": document,
                        "ACCION": row["ACCION"],
                    }
                )
    guardar_contador(contador)
    expanded_df = DataFrame(new_rows)
    return expanded_df


def load_and_transform_transfer_excel(file_path):
    """Carga el archivo en un DataFrame y realiza las transformaciones necesarias"""
    df = read_excel(file_path, dtype=str)
    df = df[["NOMBRE", "ID OFAC"]]
    return df


def compare_lists(df, transfer):
    """Compara listas y encuentra los mejores matches, agregando columnas de comparacion"""
    mask_modify = df["ACCION"] == "modify"
    df.loc[mask_modify, "ID OFAC COMPARADO"] = df.loc[mask_modify, "ID OFAC"]
    df.loc[mask_modify, "COMPARADO"] = df.loc[mask_modify, "NOMBRE COMPLETO"]
    df.loc[mask_modify, "SCORE"] = 100

    df_to_compare = df[~mask_modify]

    if not df_to_compare.empty:
        df_names_array = df_to_compare["NOMBRE COMPLETO"].fillna("N/A").values
        transfer_names_array = transfer["NOMBRE"].values
        transfer_id_array = transfer["ID OFAC"].values

        score_matrix = compare_names_matrix(df_names_array, transfer_names_array)

        best_match_indices = argmax(score_matrix, axis=1)
        best_scores = max(score_matrix, axis=1)

        df.loc[~mask_modify, "ID OFAC COMPARADO"] = transfer_id_array[best_match_indices]
        df.loc[~mask_modify, "COMPARADO"] = transfer_names_array[best_match_indices]
        df.loc[~mask_modify, "SCORE"] = best_scores * 100

    return df


def generate_comparison_file_ofac(file_name, pub_date):
    """Genera la comparación de nombres y documentos con el archivo Transfer"""

    try:
        df = read_excel(f"./output_files/{file_name}", dtype=str)
    except Exception as e:
        print(e)
        raise CustomError(f"Lectura del archivo: {file_name}")

    yield True  # Leer archivo

    try:
        process_aliases(df)
        process_documents(df)
        filter_names(df)
        filter_documents(df)

    except Exception as e:
        print(e)
        raise CustomError("Procesamiento de nombres, alias y documentos.")

    yield True  # Procesar Nombres, Alias y Documentos

    try:
        df = expand_dataframe(df)
    except Exception as e:
        print(e)
        raise CustomError("Intentando expandir el DataFrame.")

    try:
        transfer = load_and_transform_transfer_excel(TRANSFER_PATH)
    except Exception as e:
        print(e)
        raise CustomError(f"❌ No se pudo cargar el archivo de transferencias: {TRANSFER_PATH}")

    try:
        final = compare_lists(df, transfer)
    except Exception as e:
        print(e)
        raise CustomError("Comparación de los nombres.")

    yield True  # Comparar nombres

    try:
        filename = f"OFAC_Transfer_{pub_date}.xlsx"
        save_to_excel(final, filename)
    except Exception:
        raise CustomError(f"Proceso de guardado el archivo final: {filename}")

    yield True  # Guardar Archivo Final

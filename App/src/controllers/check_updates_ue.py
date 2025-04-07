from src.models.api_consumer import fetch_data
from src.util.error import CustomError
from datetime import datetime
from src.util.excel_helper import save_to_excel
from pandas import read_csv, to_datetime
from io import StringIO
from src.util.data_helpers import is_latin_or_punctuation


URL_DATA = "https://webgate.ec.europa.eu/fsd/fsf/public/files/csvFullSanctionsList_1_1/content?token=dG9rZW4tMjAxNw"


def transform_data(data, fecha):
    columnas_necesarias = [
        "Identification_Number",
        "NameAlias_WholeName",
        "NameAlias_NameLanguage",
        "Entity_Regulation_PublicationDate",
    ]

    df = read_csv(StringIO(data), sep=";", usecols=columnas_necesarias, dtype=str)

    df["Entity_Regulation_PublicationDate"] = to_datetime(
        df["Entity_Regulation_PublicationDate"], errors="coerce"
    )

    fecha = to_datetime(fecha, format="%d/%m/%Y")

    df = df[df["Entity_Regulation_PublicationDate"] >= fecha]

    df["NameAlias_NameLanguage"] = df["NameAlias_NameLanguage"].fillna("")
    df["Identification_Number"] = df["Identification_Number"].fillna("")

    df = df[df["NameAlias_NameLanguage"].isin(["EN", "ES", ""])]

    df = df[df["NameAlias_WholeName"].notna()]
    df = df[
        df["NameAlias_WholeName"].apply(
            lambda x: all(is_latin_or_punctuation(ch) for ch in x)
        )
    ]

    df = df[
        [
            "Entity_Regulation_PublicationDate",
            "Identification_Number",
            "NameAlias_WholeName",
        ]
    ].rename(
        columns={
            "Entity_Regulation_PublicationDate": "DATE",
            "Identification_Number": "ID",
            "NameAlias_WholeName": "NOMBRE COMPLETO",
        }
    )

    df = df.astype(str)

    return df.sort_values("DATE")


def generate_update_file_ue(fecha):
    try:
        data = None
        try:
            data = fetch_data(URL_DATA)
        except Exception:
            raise CustomError("Descarga de los datos.")

        yield True  # Confirmar descarga

        try:
            df = transform_data(data, fecha)
        except Exception:
            raise CustomError("Transformación los datos.")

        try:
            today_date = datetime.today().strftime("%Y-%m-%d")
            filename = f"UE_{today_date}.xlsx"
            save_to_excel(df, filename)
        except Exception:
            raise CustomError(f"Proceso de guardado del archivo: {filename}")

        yield filename, today_date  # Confirmar archivo

    except CustomError as e:
        raise e  # Relanza la excepción sin imprimir

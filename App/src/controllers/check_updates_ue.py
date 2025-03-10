from src.models.api_consumer import fetch_data
from src.util.error import CustomError
from datetime import datetime
from src.util.excel_helper import save_to_excel
from src.util.data_helpers import parse_xml, is_only_number
from pandas import DataFrame, read_csv, to_datetime
from io import StringIO


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
    df = df[df["NameAlias_NameLanguage"].isin(["EN", "ES", ""])]

    df = df[df["NameAlias_WholeName"].notna()]

    df = df[["Identification_Number", "NameAlias_WholeName"]].rename(
        columns={"Identification_Number": "ID", "NameAlias_WholeName": "NOMBRE"}
    )

    return df


def generate_update_file_ue(fecha):
    try:
        data = None
        try:
            with open("./Example.csv", "r", encoding="utf-8") as f:
                data = f.read()
            # data = fetch_data(URL_DATA)
        except Exception:
            raise CustomError("❌ Error al descargar los datos.")

        yield True  # Confirmar descarga

        try:
            df = transform_data(data, fecha)
        except Exception:
            raise CustomError("❌ Error al transformar los datos.")

        try:
            today_date = datetime.today().strftime("%Y-%m-%d")
            filename = f"UE_{today_date}.xlsx"
            save_to_excel(df, filename)
        except Exception:
            raise CustomError(f"❌ No se pudo guardar el archivo: {filename}")

        yield True  # Confirmar archivo

    except CustomError as e:
        raise e  # Relanza la excepción sin imprimir

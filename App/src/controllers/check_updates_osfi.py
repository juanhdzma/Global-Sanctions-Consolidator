from src.models.api_consumer import fetch_data
from src.util.error import CustomError
from datetime import datetime
from src.util.data_helpers import parse_xml
from src.util.excel_helper import save_to_excel
from pandas import DataFrame, to_datetime, Timestamp


URL_DATA = "https://www.international.gc.ca/world-monde/assets/office_docs/international_relations-relations_internationales/sanctions/sema-lmes.xml"


def extract_records(data):
    root = parse_xml(data)
    data = []
    for record in root.findall("record"):
        row = {
            child.tag: child.text.replace("\n", "").replace("\t", "").strip()
            for child in record
        }
        data.append(row)
    return DataFrame(data)


def transform_data(data, fecha):
    df = extract_records(data)
    df = df.drop(
        columns=[
            "Item",
            "Schedule",
            "Country",
            "DateOfBirthOrShipBuildDate",
            "Aliases",
            "TitleOrShip",
            "ShipIMONumber",
        ]
    )

    df["NOMBRE COMPLETO"] = df[["GivenName", "LastName", "EntityOrShip"]].apply(
        lambda row: " ".join(row.dropna()), axis=1
    )
    df = df[["DateOfListing", "NOMBRE"]]

    df.rename(columns={"DateOfListing": "DATE"}, inplace=True)
    df["DATE"] = to_datetime(df["DATE"], format="%Y-%m-%d")
    fecha = Timestamp(fecha)
    df = df[df["DATE"] >= fecha]

    df = df.astype(str)

    return df[["DATE", "NOMBRE COMPLETO"]].sort_values("DATE")


def transform_data(data, fecha):
    df = extract_records(data)
    df = df.drop(
        columns=[
            "Item",
            "Schedule",
            "Country",
            "DateOfBirthOrShipBuildDate",
            "Aliases",
            "TitleOrShip",
            "ShipIMONumber",
        ]
    )

    df["NOMBRE COMPLETO"] = df[["GivenName", "LastName", "EntityOrShip"]].apply(
        lambda row: " ".join(row.dropna()), axis=1
    )
    df = df[["DateOfListing", "NOMBRE COMPLETO"]]

    df.rename(columns={"DateOfListing": "DATE"}, inplace=True)
    df["DATE"] = to_datetime(df["DATE"], format="%Y-%m-%d")
    fecha = Timestamp(fecha)
    df = df[df["DATE"] >= fecha]

    df = df.astype(str)

    return df[["DATE", "NOMBRE COMPLETO"]].sort_values("DATE")


def generate_update_file_osfi(fecha):
    try:
        data = None
        try:
            data = fetch_data(URL_DATA)
        except Exception:
            raise CustomError("Descarga de los datos.")

        yield True  # Confirmar descarga

        try:
            df = transform_data(data, fecha)
        except Exception as e:
            raise CustomError("Transformación los datos.")

        try:
            today_date = datetime.today().strftime("%Y-%m-%d")
            filename = f"OSFI_{today_date}.xlsx"
            save_to_excel(df, filename)
        except Exception:
            raise CustomError(f"Proceso de guardado del archivo: {filename}")

        yield filename, today_date  # Confirmar archivo

    except CustomError as e:
        raise e  # Relanza la excepción sin imprimir

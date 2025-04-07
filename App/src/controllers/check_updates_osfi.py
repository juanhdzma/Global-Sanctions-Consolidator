from src.models.api_consumer import fetch_data
from src.util.error import CustomError
from datetime import datetime
from src.util.data_helpers import parse_xml
from src.util.excel_helper import save_to_excel
from pandas import DataFrame, to_datetime, Timestamp


URL_DATA = "https://www.international.gc.ca/world-monde/assets/office_docs/international_relations-relations_internationales/sanctions/sema-lmes.xml"


def extract_records(data):
    root = parse_xml(data)
    ns = {"ss": "urn:schemas-microsoft-com:office:spreadsheet"}

    rows = []
    for row in root.findall(".//ss:Worksheet/ss:Table/ss:Row", ns):
        row_data = []
        for cell in row.findall("ss:Cell", ns):
            data_node = cell.find("ss:Data", ns)
            value = (
                data_node.text.strip()
                if data_node is not None and data_node.text
                else ""
            )
            row_data.append(value)
        rows.append(row_data)

    df = DataFrame(rows)
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)
    return df


def transform_data(data, fecha):
    df = extract_records(data)
    keywords = [
        "Item",
        "Schedule",
        "Country",
        "DateOfBirth",
        "Ship build",
        "Aliases",
        "Title or Ship",
        "Ship IMO",
    ]

    cols_to_drop = [
        col for col in df.columns if col and any(kw in col for kw in keywords)
    ]

    df = df.drop(columns=cols_to_drop)

    name_keywords = ["Given", "Last", "Entity"]

    name_cols = [
        col for col in df.columns if col and any(kw in col for kw in name_keywords)
    ]

    df["NOMBRE COMPLETO"] = df[name_cols].apply(
        lambda row: " ".join(row.dropna().astype(str)), axis=1
    )

    df.rename(
        columns={
            "Date of Listing (YYYY/MM/DD) / Date d'inscription (AAAA/MM/JJ)": "DATE"
        },
        inplace=True,
    )

    df = df[
        [
            "DATE",
            "NOMBRE COMPLETO",
        ]
    ]

    df["DATE"] = to_datetime(df["DATE"], format="ISO8601", errors="coerce")
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
            print(e)
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

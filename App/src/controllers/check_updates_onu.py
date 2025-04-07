from src.models.api_consumer import fetch_data
from src.util.error import CustomError
from datetime import datetime
from src.util.data_helpers import parse_xml
from src.util.excel_helper import save_to_excel
from pandas import DataFrame, to_datetime, Timestamp


URL_DATA = "https://scsanctions.un.org/resources/xml/en/consolidated.xml?_gl=1*16se66c*_ga*NTkyODE5NjE2LjE3NDIyNDMyMzk.*_ga_TK9BQL5X7Z*MTc0MjI0MzIzOS4xLjAuMTc0MjI0MzM1Ny4wLjAuMA.."


def extract_records(root):
    section = {"ENTITY": root.find("ENTITIES"), "INDIVIDUAL": root.find("INDIVIDUALS")}
    final_list = []
    for key, value in section.items():
        if value is None:
            continue
        for item in value.findall(key):
            first_name = item.findtext("FIRST_NAME", "").strip()
            second_name = item.findtext("SECOND_NAME", "").strip()
            third_name = item.findtext("THIRD_NAME", "").strip()
            fourth_name = item.findtext("FOURTH_NAME", "").strip()
            full_name = " ".join(
                filter(None, [first_name, second_name, third_name, fourth_name])
            )
            listed_on = item.find("LISTED_ON")
            last_day_updated_section = item.find("LAST_DAY_UPDATED")
            if last_day_updated_section is not None and listed_on is not None:
                last_dates = [
                    value.text
                    for value in last_day_updated_section.findall("VALUE")
                    if value.text
                ]
                latest_date = max(last_dates) if last_dates else listed_on.text.strip()
            else:
                latest_date = "NA"
            row = {"DATE": latest_date, "NOMBRE COMPLETO": full_name}
            final_list.append(row)
    return DataFrame(final_list)


def transform_data(data, fecha):
    root = parse_xml(data)
    df = extract_records(root)

    df["DATE"] = to_datetime(df["DATE"], format="%Y-%m-%d", errors="coerce")
    date = Timestamp("2024-09-16")

    df = df[df["DATE"] >= date]

    df = df.astype(str)

    return df[["DATE", "NOMBRE COMPLETO"]].sort_values("DATE")


def generate_update_file_onu(fecha):
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
            filename = f"ONU_{today_date}.xlsx"
            save_to_excel(df, filename)
        except Exception:
            raise CustomError(f"Proceso de guardado del archivo: {filename}")

        yield filename, today_date  # Confirmar archivo

    except CustomError as e:
        raise e  # Relanza la excepción sin imprimir

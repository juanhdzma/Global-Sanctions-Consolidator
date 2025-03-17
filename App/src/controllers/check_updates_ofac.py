from src.models.api_consumer import fetch_data
from src.util.error import CustomError
from src.util.excel_helper import save_to_excel
from src.util.data_helpers import parse_xml, is_only_number, extract_pub_ids
from pandas import DataFrame, read_excel, concat


URL_DATA = "https://sanctionslistservice.ofac.treas.gov/changes/"
URL_HISTORY = "https://sanctionslistservice.ofac.treas.gov/changes/history/"
NAMESPACE = {"ns": "https://www.treasury.gov/ofac/DeltaFile/1.0"}


def transform_data(content):
    """Transforma el XML en un DataFrame, retorna el DataFrame y la fecha de publicación"""
    root = parse_xml(content)
    entities = root.findall("ns:entities/ns:entity", NAMESPACE)
    data = [extract_entity_data(entity) for entity in entities]
    return DataFrame(data), extract_publication_date(root)


def transform_just_data(content):
    """Transforma el XML en un DataFrame, retorna el DataFrame"""
    root = parse_xml(content)
    entities = root.findall("ns:entities/ns:entity", NAMESPACE)
    data = [extract_entity_data(entity) for entity in entities]
    return DataFrame(data)


def extract_publication_date(root):
    """Extrae la fecha de publicación del XML"""
    date_element = root.find("ns:publicationInfo/ns:datePublished", NAMESPACE)
    return (
        date_element.text.split("T")[0]
        if date_element is not None
        else "Fecha_no_disponible"
    )


def get_ofac_name(entity_id):
    """Obtiene el nombre de la entidad en la lista OFAC"""
    df = read_excel("./Transfer.xlsx", dtype=str)
    df = df[df["ID OFAC"] == str(entity_id)]
    if not df.empty:
        return df.iloc[0]["NOMBRE"]
    return ""


def extract_entity_data(entity):
    """Extrae la informacion de una entiendad XML"""
    action = entity.get("action", "modify")
    entity_id = entity.get("id", "N/A")

    alias_text = []
    full_name_text = ""

    for name in entity.findall(".//ns:name", NAMESPACE):
        alias_type = name.find("ns:aliasType", NAMESPACE)
        full_name = name.find(
            ".//ns:translation[ns:script='Latin']/ns:formattedFullName", NAMESPACE
        )
        full_name = full_name.text if full_name is not None else "N/A"

        if alias_type != None:
            alias_text.append(full_name)
        else:
            if full_name_text == "":
                full_name_text = full_name

    if full_name_text == "" and entity_id != "N/A":
        full_name_text = get_ofac_name(entity_id)

    doc_text = []
    for doc in entity.findall("ns:identityDocuments/ns:identityDocument", NAMESPACE):
        if doc is not None:
            doc_type = doc.find("ns:type", NAMESPACE)
            doc_type_text = doc_type.text if doc_type is not None else "N/A"

            doc_number = doc.find("ns:documentNumber", NAMESPACE)
            doc_number_text = doc_number.text if doc_number is not None else "N/A"

            issuing_country = doc.find("ns:issuingCountry", NAMESPACE)
            issuing_country_text = (
                issuing_country.text if issuing_country is not None else "N/A"
            )

            if issuing_country_text == "Colombia":
                if doc_type_text == "Cedula No.":
                    doc_text.append(f"CC {doc_number_text}")
                elif doc_type_text == "NIT #":
                    doc_text.append(f"NIT {doc_number_text}")
            elif doc_type_text == "Passport":
                if is_only_number(doc_number_text):
                    doc_text.append(f"PAS {doc_number_text}")
                else:
                    doc_text.append(f"{doc_type_text} {doc_number_text}")
            else:
                doc_text.append(f"{doc_type_text} {doc_number_text}")
        else:
            doc_text.append("N/A")
    return {
        "ID OFAC": entity_id,
        "Nombre Completo": full_name_text,
        "Documentos": doc_text,
        "Alias": alias_text,
        "Accion": action,
    }


def generate_update_file_ofac(fecha_especifica):
    try:
        pub_list = None
        try:
            if fecha_especifica:
                year = fecha_especifica.split("-")[0]
                pub_list = extract_pub_ids(
                    fetch_data(URL_HISTORY + year), fecha_especifica
                )
        except Exception as e:
            raise CustomError("Descarga de historial de publicaciones")

        data = None
        try:
            print(pub_list)
            if fecha_especifica:
                data = [fetch_data(URL_DATA + str(pub)) for pub in pub_list]
            else:
                data = fetch_data(URL_DATA + "latest")
        except Exception as e:
            print(e)
            raise CustomError("Descarga de los datos.")

        yield True  # Confirmar descarga

        try:
            if fecha_especifica:
                pub_date = fecha_especifica
                df = [transform_just_data(i) for i in data]
                df = concat(df, ignore_index=True)
            else:
                df, pub_date = transform_data(data)
        except Exception:
            raise CustomError("Transformación de los datos.")

        try:
            filename = f"OFAC_{pub_date}.xlsx"
            save_to_excel(df, filename)
        except Exception:
            raise CustomError(f"Proceso de guardado del archivo: {filename}")

        yield filename, pub_date  # Confirmar guardado

    except CustomError as e:
        raise e  # Relanza la excepción sin imprimir

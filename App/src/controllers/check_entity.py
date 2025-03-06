from src.models.api_consumer import fetch_data
from src.util.error import CustomError
from src.util.excel_helper import save_to_excel
from src.util.data_helpers import parse_xml, is_only_number
from pandas import DataFrame


URL_DATA = "https://sanctionslistservice.ofac.treas.gov/entities"
NAMESPACE = {
    "ns": "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/ENHANCED_XML"
}


def transform_data(content):
    """Transforma el XML en un DataFrame, retorna el DataFrame y la fecha de publicación"""
    root = parse_xml(content)
    entities = root.findall("ns:entities/ns:entity", NAMESPACE)
    data = [extract_entity_data(entity) for entity in entities]
    return DataFrame(data), extract_publication_date(root)


def extract_publication_date(root):
    """Extrae la fecha de publicación del XML"""
    date_element = root.find("ns:publicationInfo/ns:dataAsOf", NAMESPACE)
    return (
        date_element.text.split("T")[0]
        if date_element is not None
        else "Fecha_no_disponible"
    )


def extract_entity_data(entity):
    """Extrae la informacion de una entiendad XML"""
    entity_id = entity.get("id", "N/A")

    alias_text = []
    full_name_text = "N/A"

    for name in entity.findall(".//ns:name", NAMESPACE):
        alias_type = name.find("ns:aliasType", NAMESPACE)
        full_name = name.find(
            ".//ns:translation[ns:script='Latin']/ns:formattedFullName", NAMESPACE
        )
        full_name = full_name.text if full_name is not None else "N/A"

        if alias_type != None:
            alias_text.append(full_name)
        else:
            if full_name_text == "N/A":
                full_name_text = full_name

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
        "NOMBRE": full_name_text,
        "DOCUMENTOS": doc_text,
        "ALIAS": alias_text,
    }


def generate_entity_file():
    try:
        data_yield = fetch_data(URL_DATA)

        try:
            yield next(data_yield)  # Tamaño del archivo
            data = next(data_yield)  # Contenido del archivo
        except Exception:
            raise CustomError("❌ Error al descargar los datos.")

        yield True  # Confirmar descarga

        try:
            df, pub_date = transform_data(data)
        except Exception:
            raise CustomError("❌ Error al transformar los datos.")

        try:
            filename = f"Entity_{pub_date}.xlsx"
            save_to_excel(df, filename)
        except Exception:
            raise CustomError(f"❌ No se pudo guardar el archivo: {filename}")

        yield True  # Confirmar guardado

    except CustomError as e:
        raise e  # Relanza la excepción sin imprimir

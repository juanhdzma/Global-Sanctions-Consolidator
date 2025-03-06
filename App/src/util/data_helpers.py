from lxml import etree
from re import fullmatch, search, sub


def parse_xml(content):
    """Parsea el contenido XML y devuelve el elemento raiz"""
    return etree.fromstring(content)


def is_only_number(text):
    """Verifica si el texto contiene solo números"""
    return bool(fullmatch(r"\d+", text))


def clean_strings(s):
    """Limpia la cadena eliminando caracteres especiales, numeros y espacios"""
    return sub(r"[^a-zA-Z]", "", s)


def verify_if_contain_number(s):
    """Verifica si el texto tiene algun numero"""
    return search(r"\d", s)

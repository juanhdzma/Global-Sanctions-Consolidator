from lxml import etree
from re import fullmatch, search, sub, match
from pandas import read_json, to_datetime
from io import StringIO
import os


ARCHIVO_CONTADOR = "./Contador.txt"


def parse_xml(content):
    """Parsea el contenido XML y devuelve el elemento raiz"""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return etree.fromstring(content)


def is_only_number(text):
    """Verifica si el texto contiene solo números"""
    return bool(fullmatch(r"\d+", text))


def clean_strings(s):
    """Limpia la cadena eliminando caracteres especiales, numeros y espacios"""
    return sub(r"[^a-zA-Z]", "", s)


def extract_pub_ids(s, date):
    df = read_json(StringIO(s))
    lista_pub = df[to_datetime(df["datePublished"]).dt.strftime("%Y-%m-%d") == date][
        "publicationID"
    ].tolist()
    return lista_pub


def is_latin_or_punctuation(text):
    return all(
        match(r"[a-zA-ZÀ-ÿ0-9\s.,;:'\"!?()\[\]{}\-_/\\@#\$%\^&\*\+=<>|~`]", ch)
        for ch in text
    )


def leer_contador():
    if os.path.exists(ARCHIVO_CONTADOR):
        with open(ARCHIVO_CONTADOR, "r") as f:
            return int(f.read())
    else:
        return 0


def guardar_contador(valor):
    with open(ARCHIVO_CONTADOR, "w") as f:
        f.write(str(valor))


def format_name(nombre):
    # Permite letras y espacios, convierte todo a mayúsculas
    limpio = "".join(c for c in nombre if c.isalpha() or c.isspace())
    return limpio.upper()

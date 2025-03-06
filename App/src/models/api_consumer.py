from requests import get
from requests.exceptions import RequestException
from src.util.error import CustomError
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning


def fetch_data(url_data):
    """Solicita el contenido XML desde el servidor y retorna el tamaño del archivo y el contenido."""
    try:
        disable_warnings(InsecureRequestWarning)

        with get(url_data, verify=False, stream=True) as response:
            response.raise_for_status()

            file_size = response.headers.get("Content-Length")
            if file_size:
                yield int(file_size) / (1024 * 1024)
            else:
                yield "Desconocido"
            yield response.content
    except RequestException:
        raise CustomError(f"❌ Error al solicitar el contenido de la API: {url_data}")

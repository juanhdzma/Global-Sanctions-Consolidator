from src.util.error import CustomError
import subprocess
import shlex


USE_PROXY = False
PROXY = "http://127.0.0.1:8000"


def fetch_data(url_data):
    try:
        curl_base = "curl -s -k -L"
        if USE_PROXY:
            curl_base += f" -x {shlex.quote(PROXY)}"

        cmd_content = f"{curl_base} {shlex.quote(url_data)}"
        result = subprocess.run(
            cmd_content, shell=True, capture_output=True, text=True, check=True
        )

        return result.stdout

    except subprocess.SubprocessError:
        raise CustomError(f"❌ Error al solicitar el contenido de la API: {url_data}")

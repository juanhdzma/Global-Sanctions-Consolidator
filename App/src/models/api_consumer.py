from src.util.error import CustomError
import subprocess


USE_PROXY = True
PROXY = "http://172.19.152.108:8000"


def fetch_data(url_data):
    try:
        curl_base = "curl -k -L"
        if USE_PROXY:
            curl_base += f" -x {PROXY}"

        cmd_content = f"{curl_base} {url_data}"
        result = subprocess.run(
            cmd_content,
            shell=True,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )

        return result.stdout

    except subprocess.SubprocessError:
        raise CustomError(f"Petición curl al contenido de la API: {url_data}")

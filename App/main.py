from src.view.front_app import Window
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

sys.path.append(str(BASE_DIR / "src"))
sys.path.append(str(BASE_DIR / "python-3" / "Lib" / "site-packages"))

app = QApplication([])
ico_path = BASE_DIR / "assets" / "Colpatria.png"
app.setWindowIcon(QIcon(str(ico_path)))

ventana = Window()
ventana.show()
app.exec()

from src.view.front_app import Window
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.join(BASE_DIR, "src"))
sys.path.append(os.path.join(BASE_DIR, "python-3", "Lib", "site-packages"))

app = QApplication([])
ico_path = os.path.join(
    os.path.dirname(sys.modules[__name__].__file__), "assets/Colpatria.png"
)
app.setWindowIcon(QIcon(ico_path))

ventana = Window()
ventana.show()
app.exec()

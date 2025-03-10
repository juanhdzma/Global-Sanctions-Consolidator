from src.view.front_app import Window
from PyQt6.QtWidgets import QApplication
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.join(BASE_DIR, "src"))
sys.path.append(os.path.join(BASE_DIR, "python-3", "Lib", "site-packages"))

app = QApplication([])
ventana = Window()
ventana.show()
app.exec()

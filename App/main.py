import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.join(BASE_DIR, "src"))
sys.path.append(os.path.join(BASE_DIR, "python-3", "Lib", "site-packages"))


from PyQt6.QtWidgets import QApplication
from src.view.front_app import Window


app = QApplication([])
ventana = Window()
ventana.show()
app.exec()

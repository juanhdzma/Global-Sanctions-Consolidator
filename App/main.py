from PyQt6.QtWidgets import QApplication

from src.view.front_app import Window


app = QApplication([])
ventana = Window()
ventana.show()
app.exec()

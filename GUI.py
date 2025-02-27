import sys
import time
import random
import threading
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QProgressBar
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer, pyqtSignal


class MiVentana(QWidget):
    actualizar_signal = pyqtSignal(str, int)
    finalizar_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()

        # Conectar señales a métodos
        self.actualizar_signal.connect(self.animar_progreso)
        self.finalizar_signal.connect(self.finalizar_proceso)

        self.progreso_actual = 0  # Para animar la barra de progreso

    def initUI(self):
        self.setWindowTitle("Interfaz Moderna con PyQt6")
        self.setFixedSize(600, 400)
        self.setStyleSheet(
            "background-color: #222; color: white; font-size: 14px;")

        # Centrar la ventana en la pantalla
        self.centrar_ventana()

        layout = QVBoxLayout()

        # Botón ejecutar
        self.boton = QPushButton("Ejecutar")
        self.boton.setFont(QFont("Arial", 12))
        self.boton.setStyleSheet("""
            QPushButton {
                background-color: #007BFF; color: white; padding: 10px; border-radius: 5px;
            }
            QPushButton:disabled {
                background-color: #555; color: #AAA;
            }
        """)
        self.boton.clicked.connect(self.ejecutar)
        layout.addWidget(self.boton)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #444;
                border-radius: 5px;
                background-color: #333;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #007BFF;
                width: 10px;
            }
        """)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Consola (texto)
        self.consola = QTextEdit()
        self.consola.setFont(QFont("Courier", 11))
        self.consola.setReadOnly(True)
        self.consola.setStyleSheet(
            "background-color: #333; color: #0F0; padding: 5px; border-radius: 5px;")
        layout.addWidget(self.consola)

        self.setLayout(layout)

    def centrar_ventana(self):
        pantalla = QApplication.primaryScreen().geometry()
        ventana = self.frameGeometry()
        ventana.moveCenter(pantalla.center())
        self.move(ventana.topLeft())

    def ejecutar(self):
        self.boton.setEnabled(False)
        self.consola.clear()
        self.progress_bar.setValue(0)
        self.progreso_actual = 0
        self.consola.append("Ejecutando proceso...\n")

        hilo = threading.Thread(target=self.proceso, daemon=True)
        hilo.start()

    def proceso(self):
        pasos = [
            ("Paso 1: Cargando datos...", 30),
            ("Paso 2: Procesando información...", 60),
            ("Paso 3: Finalizando operación...", 100),
        ]

        for texto, progreso in pasos:
            time.sleep(1)
            self.actualizar_signal.emit(texto, progreso)

        resultado = random.choice(["exito", "error"])
        time.sleep(1)

        if resultado == "exito":
            self.finalizar_signal.emit("✅ Proceso finalizado correctamente.")
        else:
            self.finalizar_signal.emit("❌ Error en el proceso.")

    def animar_progreso(self, texto, progreso_final):
        self.consola.append(texto)

        # Crear un temporizador para animar la barra de progreso
        self.timer = QTimer(self)
        self.timer.timeout.connect(
            lambda: self.incrementar_progreso(progreso_final))
        self.timer.start(30)  # Cada 30ms se incrementa un poco

    def incrementar_progreso(self, progreso_final):
        if self.progreso_actual < progreso_final:
            self.progreso_actual += 1
            self.progress_bar.setValue(self.progreso_actual)
        else:
            self.timer.stop()

    def finalizar_proceso(self, mensaje):
        self.consola.append(mensaje)
        self.progress_bar.setValue(100)
        self.boton.setEnabled(True)


# Lanzar aplicación
app = QApplication(sys.argv)
ventana = MiVentana()
ventana.show()
sys.exit(app.exec())

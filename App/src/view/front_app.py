from threading import Thread
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QWidget, QVBoxLayout, QPushButton, QTextEdit, QProgressBar
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import QTimer, pyqtSignal
from src.controllers.check_entity import generate_entity_file
from src.controllers.check_updates import generate_update_file
from src.controllers.check_transfer import generate_comparison_file


class Window(QWidget):
    actualizar_signal = pyqtSignal(str, int)
    finalizar_signal = pyqtSignal(str, bool)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.actualizar_signal.connect(self.animar_progreso)
        self.finalizar_signal.connect(self.finalizar_proceso)
        self.progreso_actual = 0
        self.timer = QTimer(self)

    def initUI(self):
        self.setWindowTitle("API SANCIONES OFAC")
        self.setFixedSize(600, 400)
        self.setStyleSheet(
            "background-color: #222; color: white; font-size: 14px;")
        self.setWindowIcon(QIcon(".../assets/OFAC.ico"))
        self.centrar_ventana()

        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        self.boton_actualizacion = self.crear_boton(
            "Ejecutar Actualización", self.ejecutar_actualizacion)
        button_layout.addWidget(self.boton_actualizacion)

        self.boton_entidades = self.crear_boton(
            "Ejecutar Entidades", self.ejecutar_entidades)
        button_layout.addWidget(self.boton_entidades)

        layout.addLayout(button_layout)
        self.progress_bar = self.crear_progress_bar()
        layout.addWidget(self.progress_bar)
        self.consola = self.crear_consola()
        layout.addWidget(self.consola)
        self.setLayout(layout)

    def centrar_ventana(self):
        screen = QApplication.primaryScreen().geometry()
        window = self.frameGeometry()
        window.moveCenter(screen.center())
        self.move(window.topLeft())

    def crear_boton(self, texto, funcion):
        boton = QPushButton(texto)
        boton.setFont(QFont("Arial", 12))
        boton.setStyleSheet("""
            QPushButton {
                background-color: #007BFF; color: white; padding: 10px; border-radius: 5px;
            }
            QPushButton:disabled {
                background-color: #555; color: #AAA;
            }
        """)
        boton.clicked.connect(funcion)
        return boton

    def crear_progress_bar(self):
        progress_bar = QProgressBar()
        progress_bar.setStyleSheet("""
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
        progress_bar.setValue(0)
        return progress_bar

    def crear_consola(self):
        consola = QTextEdit()
        consola.setFont(QFont("Arial", 11))
        consola.setReadOnly(True)
        consola.setStyleSheet(
            "background-color: #333; color: #007BFF; padding: 5px; border-radius: 5px;")
        return consola

    def ejecutar_actualizacion(self):
        self.desactivar_botones()
        self.limpiar_estado()
        self.consola.append("Ejecutando actualización...")
        hilo = Thread(target=self.proceso_actualizacion, daemon=True)
        hilo.start()

    def ejecutar_entidades(self):
        self.desactivar_botones()
        self.limpiar_estado()
        self.consola.append("Ejecutando entidades...")
        hilo = Thread(target=self.proceso_entidades, daemon=True)
        hilo.start()

    def desactivar_botones(self):
        self.boton_actualizacion.setEnabled(False)
        self.boton_entidades.setEnabled(False)

    def activar_botones(self):
        self.boton_actualizacion.setEnabled(True)
        self.boton_entidades.setEnabled(True)

    def limpiar_estado(self):
        self.progress_bar.setValue(0)
        self.progreso_actual = 0
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
        self.consola.clear()

    def actualizar_estado(self, mensaje, progreso_final):
        self.actualizar_signal.emit(mensaje, progreso_final)

    def animar_progreso(self, mensaje, progreso_final):
        self.consola.append(mensaje)
        self.timer.stop()
        try:
            self.timer.timeout.disconnect()
        except TypeError:
            pass
        self.timer.timeout.connect(
            lambda: self.incrementar_progreso(progreso_final))
        self.timer.start(5)

    def incrementar_progreso(self, progreso_final):
        if self.progreso_actual < progreso_final:
            self.progreso_actual += 1
            self.progress_bar.setValue(self.progreso_actual)
        else:
            self.timer.stop()

    def finalizar_proceso(self, mensaje, exito):
        self.consola.append(mensaje)
        self.progress_bar.setValue(100)
        if exito:
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #444;
                    border-radius: 5px;
                    background-color: #333;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #28a745;
                    width: 10px;
                }
            """)
        else:
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #444;
                    border-radius: 5px;
                    background-color: #333;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #DC3545;
                    width: 10px;
                }
            """)

        self.activar_botones()

    def proceso_actualizacion(self):
        try:
            self.actualizar_estado(
                "", 10)

            self.actualizar_estado(
                "Empezando proceso de verificar actualizaciones...", 10)
            data_update = generate_update_file()
            file_size = next(data_update)
            self.actualizar_estado(
                f"Tamaño del archivo: {file_size:.2f} MB", 5)
            if next(data_update):
                self.actualizar_estado("Archivo descargado correctamente", 20)
            file_name, pub_date = next(data_update)
            if file_name:
                self.actualizar_estado("Archivo guardado correctamente", 45)

            self.actualizar_estado(
                "", 45)

            self.actualizar_estado(
                "Empezando proceso de procesar documento y generar coincidencias...", 50)
            data_update = generate_comparison_file(file_name, pub_date)
            if next(data_update):
                self.actualizar_estado("Archivo leído correctamente", 60)
            if next(data_update):
                self.actualizar_estado(
                    "Nombres, alias y documentos procesados correctamente", 75)
            if next(data_update):
                self.actualizar_estado(
                    "Comparación con transfer completada", 90)
            if next(data_update):
                self.actualizar_estado(
                    "Archivo de comparación guardado correctamente", 100)

            self.finalizar_signal.emit(
                "✅ Proceso finalizado correctamente.", True)

        except Exception as e:
            self.finalizar_signal.emit(str(e), False)

    def proceso_entidades(self):
        try:
            self.actualizar_estado(
                "", 10)

            self.actualizar_estado(
                "Empezando proceso de descargar entidades...", 10)
            data_update = generate_entity_file()
            file_size = next(data_update)
            self.actualizar_estado(
                f"Tamaño del archivo: {file_size:.2f} MB", 20)
            if next(data_update):
                self.actualizar_estado("Archivo descargado correctamente", 90)
            file_name = next(data_update)
            if file_name:
                self.actualizar_estado("Archivo guardado correctamente", 100)

            self.finalizar_signal.emit(
                "✅ Proceso finalizado correctamente.", True)

        except Exception as e:
            self.finalizar_signal.emit(str(e), False)

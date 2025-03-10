from threading import Thread
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QProgressBar,
    QLabel,
    QGridLayout,
    QDateEdit,
    QCalendarWidget,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QTimer, pyqtSignal, Qt, QDate, QLocale
from src.controllers.check_entity_ofac import generate_entity_file_ofac
from src.controllers.check_updates_ofac import generate_update_file_ofac
from src.controllers.check_transfer_ofac import generate_comparison_file_ofac


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

    ############ INICIALIZACIÓN DE LA INTERFAZ ############

    def initUI(self):
        self.setWindowTitle("Global Sanctions Consolidator")
        self.setFixedSize(800, 500)
        self.setStyleSheet("background-color: #222; color: white; font-size: 14px;")
        self.centrar_ventana()

        layout = QVBoxLayout()
        grid_layout = QGridLayout()

        secciones = {
            "OFAC": {
                "Ejecutar Actualización OFAC": "ejecutar_actualizacion_ofac",
                "Ejecutar Entidades OFAC": "ejecutar_entidades_ofac",
            },
            "Union Europea": {
                "Ejecutar Actualización UE": "ejecutar_actualizacion_ue",
                "Fecha": "NA",
            },
            "Naciones Unidas": {"Ejecutar ONU": "ejecutar_actualizacion_onu"},
            "OSFI": {"Ejecutar OSFI": "ejecutar_actualizacion_osfi"},
        }

        self.botones = {}
        row, col = 0, 0

        for seccion, botones in secciones.items():
            label = QLabel(seccion)
            label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            label.setStyleSheet(
                """
                color: #FFF;
                text-align: center;
                border: 1px solid white;
                padding: 5px;
                """
            )
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            span = max(len(botones), 2)
            grid_layout.addWidget(label, row, col, 1, span)

            for i, (boton_texto, funcion_nombre) in enumerate(botones.items()):
                funcion = getattr(self, funcion_nombre, None)
                if boton_texto == "Fecha":
                    boton = self.crear_selector_fecha(seccion)
                else:
                    boton = self.crear_boton(boton_texto, funcion)
                grid_layout.addWidget(
                    boton,
                    row + 1,
                    col + i * (2 if len(botones) == 1 else 1),
                    1,
                    2 if len(botones) == 1 else 1,
                )
                self.botones[boton_texto] = boton

            col += 2
            if col >= 4:
                col = 0
                row += 2

        layout.addLayout(grid_layout)
        self.progress_bar = self.crear_progress_bar()
        layout.addWidget(self.progress_bar)
        self.consola = self.crear_consola()
        layout.addWidget(self.consola)
        self.setLayout(layout)

    def crear_selector_fecha(self, area):
        selector = QDateEdit()
        selector.setObjectName(f"selector_{area}")
        selector.setCalendarPopup(True)

        estilo = """
            QDateEdit {
                background-color: #333;
                color: white;
                padding: 6px;
                border-radius: 4px;
                border: 1px solid #555;
            }
        """

        selector.setStyleSheet(estilo)

        calendario = selector.calendarWidget()
        calendario.setLocale(QLocale(QLocale.Language.Spanish))

        hoy = QDate.currentDate()
        selector.setDate(hoy)
        selector.setMaximumDate(hoy)

        return selector

    def centrar_ventana(self):
        screen = QApplication.primaryScreen().geometry()
        window = self.frameGeometry()
        window.moveCenter(screen.center())
        self.move(window.topLeft())

    def crear_boton(self, texto, funcion):
        boton = QPushButton(texto)
        boton.setFont(QFont("Arial", 12))
        boton.setStyleSheet(
            """
            QPushButton {
                background-color: #007BFF; color: white; padding: 10px; border-radius: 5px;
            }
            QPushButton:disabled {
                background-color: #555; color: #AAA;
            }
            """
        )
        if funcion:
            boton.clicked.connect(funcion)
        return boton

    def crear_progress_bar(self):
        progress_bar = QProgressBar()
        progress_bar.setStyleSheet(
            """
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
        """
        )
        progress_bar.setValue(0)
        return progress_bar

    def crear_consola(self):
        consola = QTextEdit()
        consola.setFont(QFont("Arial", 11))
        consola.setReadOnly(True)
        consola.setStyleSheet(
            "background-color: #333; color: #007BFF; padding: 5px; border-radius: 5px;"
        )
        return consola

    ############ CONTROL DE PROGRESO Y ANIMACIONES ############

    def desactivar_botones(self):
        for boton in self.botones.values():
            boton.setEnabled(False)

    def activar_botones(self):
        for boton in self.botones.values():
            boton.setEnabled(True)

    def limpiar_estado(self):
        self.progress_bar.setValue(0)
        self.progreso_actual = 0
        self.progress_bar.setStyleSheet(
            """
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
        """
        )
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
        self.timer.timeout.connect(lambda: self.incrementar_progreso(progreso_final))
        self.timer.start(5)

    def incrementar_progreso(self, progreso_final):
        if self.progreso_actual < progreso_final:
            self.progreso_actual += 1
            self.progress_bar.setValue(self.progreso_actual)
        else:
            self.timer.stop()

    def finalizar_proceso(self, mensaje, exito):
        self.consola.append("")
        self.consola.append(mensaje)
        self.progress_bar.setValue(100)
        if exito:
            self.progress_bar.setStyleSheet(
                """
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
            """
            )
        else:
            self.progress_bar.setStyleSheet(
                """
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
            """
            )

        self.activar_botones()

    ############ PROCESOS DE OFAC ############

    def ejecutar_actualizacion_ofac(self):
        self.desactivar_botones()
        self.limpiar_estado()
        self.consola.append("Ejecutando actualización...")
        hilo = Thread(target=self.proceso_actualizacion_ofac, daemon=True)
        hilo.start()

    def ejecutar_entidades_ofac(self):
        self.desactivar_botones()
        self.limpiar_estado()
        self.consola.append("Ejecutando entidades...")
        hilo = Thread(target=self.proceso_entidades_ofac, daemon=True)
        hilo.start()

    def proceso_actualizacion_ofac(self):
        try:
            self.actualizar_estado("", 10)

            self.actualizar_estado(
                "Empezando proceso de verificar actualizaciones...", 10
            )
            data_update = generate_update_file_ofac()
            self.actualizar_estado(f"Empezando descarga del archivo", 5)
            if next(data_update):
                self.actualizar_estado("Archivo descargado correctamente", 20)
            file_name, pub_date = next(data_update)
            if file_name:
                self.actualizar_estado("Archivo guardado correctamente", 45)

            self.actualizar_estado("", 45)

            self.actualizar_estado(
                "Empezando proceso de procesar documento y generar coincidencias...", 50
            )
            data_update = generate_comparison_file_ofac(file_name, pub_date)
            if next(data_update):
                self.actualizar_estado("Archivo leído correctamente", 60)
            if next(data_update):
                self.actualizar_estado(
                    "Nombres, alias y documentos procesados correctamente", 70
                )
            if next(data_update):
                self.actualizar_estado(
                    "Archivo de pre-transfer guardado correctamente", 75
                )
            if next(data_update):
                self.actualizar_estado("Comparación con transfer completada", 90)
            if next(data_update):
                self.actualizar_estado(
                    "Archivo de comparación guardado correctamente", 100
                )

            self.finalizar_signal.emit("✅ Proceso finalizado correctamente.", True)

        except Exception as e:
            self.finalizar_signal.emit(str(e), False)

    def proceso_entidades_ofac(self):
        try:
            self.actualizar_estado("", 10)

            self.actualizar_estado("Empezando proceso de verificar entidades...", 10)
            data_update = generate_entity_file_ofac()
            self.actualizar_estado(
                f"Empezando descarga del archivo, alto volumen de datos esperados, por favor espere",
                20,
            )
            if next(data_update):
                self.actualizar_estado("Archivo descargado correctamente", 90)
            file_name = next(data_update)
            if file_name:
                self.actualizar_estado("Archivo guardado correctamente", 100)

            self.finalizar_signal.emit("✅ Proceso finalizado correctamente.", True)

        except Exception as e:
            self.finalizar_signal.emit(str(e), False)

    ############ PROCESOS DE UE ############

    def ejecutar_actualizacion_ue(self):
        self.desactivar_botones()
        self.limpiar_estado()
        self.consola.append("Ejecutando actualización...")
        hilo = Thread(target=self.proceso_actualizacion_ue, daemon=True)
        hilo.start()

    def proceso_actualizacion_ue(self):
        selector = self.findChild(QDateEdit, "selector_Union Europea")
        fecha = selector.date().toString("dd/MM/yyyy")

        self.consola.append(fecha)
        # self.finalizar_signal.emit("✅ Proceso finalizado correctamente.", True)
        # try:
        #     self.actualizar_estado("", 10)

        #     self.actualizar_estado(
        #         "Empezando proceso de verificar actualizaciones...", 10
        #     )
        #     data_update = generate_update_file_ue()
        #     self.actualizar_estado(
        #         f"Empezando descarga del archivo, alto volumen de datos esperados, por favor espere",
        #         20,
        #     )
        #     if next(data_update):
        #         self.actualizar_estado("Archivo descargado correctamente", 90)
        #     file_name = next(data_update)
        #     if file_name:
        #         self.actualizar_estado("Archivo guardado correctamente", 100)

        #     self.finalizar_signal.emit("✅ Proceso finalizado correctamente.", True)

        # except Exception as e:
        #     self.finalizar_signal.emit(str(e), False)

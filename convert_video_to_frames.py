import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLabel, QFileDialog, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class ExtractionThread(QThread):
    """
    Hilo para ejecutar la extracción de frames utilizando ffmpeg.
    Emite una señal cuando finaliza, indicando éxito o error.
    """
    finished_signal = pyqtSignal(bool, str)  # (éxito, mensaje)

    def __init__(self, video_path, parent=None):
        super().__init__(parent)
        self.video_path = video_path

    def run(self):
        try:
            # Crear carpeta de salida en la misma ruta que el video.
            video_dir = os.path.dirname(self.video_path)
            video_name = os.path.splitext(os.path.basename(self.video_path))[0]
            output_dir = os.path.join(video_dir, f"{video_name}_frames")
            os.makedirs(output_dir, exist_ok=True)

            # Construir el comando para extraer todos los frames.
            # Se numeran secuencialmente con el patrón "%05d.jpg"
            command = f'ffmpeg -i "{self.video_path}" "{os.path.join(output_dir, "%05d.jpg")}"'
            
            # Ejecutar el comando.
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                # Si hubo error, se emite señal con éxito=False
                self.finished_signal.emit(False, result.stderr)
            else:
                self.finished_signal.emit(True, "Extracción completada exitosamente.")
        except Exception as e:
            self.finished_signal.emit(False, str(e))

class FrameExtractorWindow(QMainWindow):
    """
    Ventana principal de la aplicación para extraer frames de un video.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Extractor de Frames de Video")
        self.setGeometry(100, 100, 400, 220)
        self.video_path = None
        self.thread = None

        # Configuración de la interfaz.
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignTop)
        
        # Botón para seleccionar video.
        self.btn_select = QPushButton("Seleccionar Video")
        self.btn_select.clicked.connect(self.select_video)
        layout.addWidget(self.btn_select)

        # Etiqueta para mostrar el video seleccionado.
        self.lbl_video = QLabel("No se ha seleccionado ningún video.")
        layout.addWidget(self.lbl_video)

        # Botón para iniciar la extracción.
        self.btn_start = QPushButton("Empezar Extracción")
        self.btn_start.clicked.connect(self.start_extraction)
        layout.addWidget(self.btn_start)

        # Barra de progreso en modo indeterminado.
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # Esto la pone en modo indeterminado.
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Etiqueta de estado.
        self.lbl_status = QLabel("")
        layout.addWidget(self.lbl_status)

    def select_video(self):
        """
        Abre un diálogo para seleccionar un archivo de video.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Video",
            "",
            "Videos (*.mp4 *.avi *.mov *.mkv);;Todos los archivos (*)"
        )
        if file_path:
            self.video_path = file_path
            self.lbl_video.setText(f"Video seleccionado: {os.path.basename(file_path)}")
        else:
            self.lbl_video.setText("No se ha seleccionado ningún video.")

    def start_extraction(self):
        """
        Inicia el proceso de extracción en un hilo separado.
        Desactiva los botones y muestra la barra de progreso.
        """
        if not self.video_path:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona un video primero.")
            return

        # Desactivar botones para evitar iniciar múltiples procesos
        self.btn_select.setEnabled(False)
        self.btn_start.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.lbl_status.setText("Extrayendo frames...")

        # Crear y empezar el hilo de extracción.
        self.thread = ExtractionThread(self.video_path)
        self.thread.finished_signal.connect(self.on_extraction_finished)
        self.thread.start()

    def on_extraction_finished(self, success, message):
        """
        Slot que se ejecuta al finalizar la extracción.
        Reactiva los botones, oculta la barra de progreso y muestra el resultado.
        """
        self.btn_select.setEnabled(True)
        self.btn_start.setEnabled(True)
        self.progress_bar.setVisible(False)

        if success:
            self.lbl_status.setText("Extracción completada exitosamente.")
            QMessageBox.information(self, "Éxito", "La extracción de frames ha finalizado con éxito.")
        else:
            self.lbl_status.setText("Error durante la extracción.")
            QMessageBox.critical(self, "Error", f"Ocurrió un error durante la extracción:\n{message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FrameExtractorWindow()
    window.show()
    sys.exit(app.exec_())

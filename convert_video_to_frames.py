import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLabel, QFileDialog, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QLocale

###############################################################################
#                             Internationalization                            #
###############################################################################
STRINGS = {
    "en": {
        "window_title": "Video Frame Extractor",
        "select_video": "Select Video",
        "start_extraction": "Start Extraction",
        "no_video_selected": "No video has been selected.",
        "video_selected": "Video selected: {filename}",
        "extraction_in_progress": "Extracting frames...",
        "extraction_success": "Extraction completed successfully.",
        "extraction_complete_msg": "The frame extraction finished successfully.",
        "extraction_error": "Error during extraction.",
        "extraction_error_msg": "An error occurred during extraction:\n{error}",
        "warning": "Warning",
        "please_select_video": "Please, select a video first."
    },
    "es": {
        "window_title": "Extractor de Frames de Video",
        "select_video": "Seleccionar Video",
        "start_extraction": "Empezar Extracción",
        "no_video_selected": "No se ha seleccionado ningún video.",
        "video_selected": "Video seleccionado: {filename}",
        "extraction_in_progress": "Extrayendo frames...",
        "extraction_success": "Extracción completada exitosamente.",
        "extraction_complete_msg": "La extracción de frames ha finalizado con éxito.",
        "extraction_error": "Error durante la extracción.",
        "extraction_error_msg": "Ocurrió un error durante la extracción:\n{error}",
        "warning": "Advertencia",
        "please_select_video": "Por favor, selecciona un video primero."
    },
    "de": {
        "window_title": "Video Frame Extraktor",
        "select_video": "Video auswählen",
        "start_extraction": "Extraktion starten",
        "no_video_selected": "Kein Video ausgewählt.",
        "video_selected": "Ausgewähltes Video: {filename}",
        "extraction_in_progress": "Frames werden extrahiert...",
        "extraction_success": "Extraktion erfolgreich abgeschlossen.",
        "extraction_complete_msg": "Die Frame-Extraktion wurde erfolgreich abgeschlossen.",
        "extraction_error": "Fehler bei der Extraktion.",
        "extraction_error_msg": "Bei der Extraktion ist ein Fehler aufgetreten:\n{error}",
        "warning": "Warnung",
        "please_select_video": "Bitte wählen Sie zuerst ein Video aus."
    },
    "fr": {
        "window_title": "Extracteur de Frames Vidéo",
        "select_video": "Sélectionner une vidéo",
        "start_extraction": "Démarrer l'extraction",
        "no_video_selected": "Aucune vidéo sélectionnée.",
        "video_selected": "Vidéo sélectionnée: {filename}",
        "extraction_in_progress": "Extraction des frames...",
        "extraction_success": "Extraction terminée avec succès.",
        "extraction_complete_msg": "L'extraction des frames est terminée avec succès.",
        "extraction_error": "Erreur lors de l'extraction.",
        "extraction_error_msg": "Une erreur est survenue lors de l'extraction:\n{error}",
        "warning": "Avertissement",
        "please_select_video": "Veuillez sélectionner une vidéo en premier."
    },
    "pt": {
        "window_title": "Extrator de Frames de Vídeo",
        "select_video": "Selecionar Vídeo",
        "start_extraction": "Iniciar Extração",
        "no_video_selected": "Nenhum vídeo selecionado.",
        "video_selected": "Vídeo selecionado: {filename}",
        "extraction_in_progress": "Extraindo frames...",
        "extraction_success": "Extração concluída com sucesso.",
        "extraction_complete_msg": "A extração dos frames foi concluída com sucesso.",
        "extraction_error": "Erro durante a extração.",
        "extraction_error_msg": "Ocorreu um erro durante a extração:\n{error}",
        "warning": "Aviso",
        "please_select_video": "Por favor, selecione um vídeo primeiro."
    },
    "ru": {
        "window_title": "Извлекатель кадров видео",
        "select_video": "Выбрать видео",
        "start_extraction": "Начать извлечение",
        "no_video_selected": "Видео не выбрано.",
        "video_selected": "Выбранное видео: {filename}",
        "extraction_in_progress": "Извлечение кадров...",
        "extraction_success": "Извлечение успешно завершено.",
        "extraction_complete_msg": "Извлечение кадров успешно завершено.",
        "extraction_error": "Ошибка при извлечении.",
        "extraction_error_msg": "Произошла ошибка при извлечении:\n{error}",
        "warning": "Предупреждение",
        "please_select_video": "Пожалуйста, сначала выберите видео."
    }
}

###############################################################################
#                           Extraction Thread Class                           #
###############################################################################
class ExtractionThread(QThread):
    """
    Thread to execute frame extraction using ffmpeg.
    Emits a signal when finished, indicating success or error.
    """
    finished_signal = pyqtSignal(bool, str)  # (success, message)

    def __init__(self, video_path, parent=None):
        super().__init__(parent)
        self.video_path = video_path

    def run(self):
        try:
            # Create output folder in the same directory as the video.
            video_dir = os.path.dirname(self.video_path)
            video_name = os.path.splitext(os.path.basename(self.video_path))[0]
            output_dir = os.path.join(video_dir, f"{video_name}_frames")
            os.makedirs(output_dir, exist_ok=True)

            # Build the command to extract all frames.
            # Frames are numbered sequentially using the pattern "%05d.jpg"
            command = f'ffmpeg -i "{self.video_path}" "{os.path.join(output_dir, "%05d.jpg")}"'
            
            # Execute the command.
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                # On error, emit signal with success=False.
                self.finished_signal.emit(False, result.stderr)
            else:
                self.finished_signal.emit(True, "OK")
        except Exception as e:
            self.finished_signal.emit(False, str(e))

###############################################################################
#                        Main Application Window                            #
###############################################################################
class FrameExtractorWindow(QMainWindow):
    """
    Main application window to extract frames from a video.
    """
    def __init__(self, lang="en"):
        super().__init__()
        self.lang = lang
        self.strings = STRINGS.get(self.lang, STRINGS["en"])
        self.setWindowTitle(self.strings["window_title"])
        self.setGeometry(100, 100, 400, 220)
        self.video_path = None
        self.thread = None

        # Set up the interface.
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignTop)
        
        # Button to select video.
        self.btn_select = QPushButton(self.strings["select_video"])
        self.btn_select.clicked.connect(self.select_video)
        layout.addWidget(self.btn_select)

        # Label to show the selected video.
        self.lbl_video = QLabel(self.strings["no_video_selected"])
        layout.addWidget(self.lbl_video)

        # Button to start extraction.
        self.btn_start = QPushButton(self.strings["start_extraction"])
        self.btn_start.clicked.connect(self.start_extraction)
        layout.addWidget(self.btn_start)

        # Indeterminate progress bar.
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # Indeterminate mode.
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label.
        self.lbl_status = QLabel("")
        layout.addWidget(self.lbl_status)

    def select_video(self):
        """
        Opens a dialog to select a video file.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.strings["select_video"],
            "",
            "Videos (*.mp4 *.avi *.mov *.mkv);;All files (*)"
        )
        if file_path:
            self.video_path = file_path
            self.lbl_video.setText(
                self.strings["video_selected"].format(filename=os.path.basename(file_path))
            )
        else:
            self.lbl_video.setText(self.strings["no_video_selected"])

    def start_extraction(self):
        """
        Starts the extraction process in a separate thread.
        Disables buttons and shows the progress bar.
        """
        if not self.video_path:
            QMessageBox.warning(
                self, self.strings["warning"], self.strings["please_select_video"]
            )
            return

        # Disable buttons to prevent multiple processes.
        self.btn_select.setEnabled(False)
        self.btn_start.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.lbl_status.setText(self.strings["extraction_in_progress"])

        # Create and start the extraction thread.
        self.thread = ExtractionThread(self.video_path)
        self.thread.finished_signal.connect(self.on_extraction_finished)
        self.thread.start()

    def on_extraction_finished(self, success, message):
        """
        Slot executed when extraction finishes.
        Re-enables buttons, hides the progress bar, and shows the result.
        """
        self.btn_select.setEnabled(True)
        self.btn_start.setEnabled(True)
        self.progress_bar.setVisible(False)

        if success:
            self.lbl_status.setText(self.strings["extraction_success"])
            QMessageBox.information(
                self, self.strings["extraction_success"], self.strings["extraction_complete_msg"]
            )
        else:
            self.lbl_status.setText(self.strings["extraction_error"])
            QMessageBox.critical(
                self,
                self.strings["extraction_error"],
                self.strings["extraction_error_msg"].format(error=message)
            )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Auto-detect system language using QLocale.
    sys_lang = QLocale.system().name().split('_')[0]
    # Use English by default unless the system language is one of the supported ones.
    if sys_lang not in STRINGS or sys_lang == "en":
        lang = "en"
    else:
        lang = sys_lang
    window = FrameExtractorWindow(lang=lang)
    window.show()
    sys.exit(app.exec_())

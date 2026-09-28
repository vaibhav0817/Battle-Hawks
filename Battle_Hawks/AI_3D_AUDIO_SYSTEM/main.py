import sys
import os
import soundfile as sf
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox
)


class AudioSystem(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI 3D Situational Audio System")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout()

        title = QLabel("AI-Based Adaptive Situational Audio Enhancement")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
        """)

        self.info = QLabel("No audio file selected.")

        upload_button = QPushButton("Upload Mixed Audio")
        upload_button.clicked.connect(self.upload_audio)

        layout.addWidget(title)
        layout.addWidget(self.info)
        layout.addWidget(upload_button)

        self.setLayout(layout)

    def upload_audio(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "Audio Files (*.wav *.mp3 *.flac)"
        )

        if not file_path:
            return

        try:

            audio, sample_rate = sf.read(file_path)

            duration = len(audio) / sample_rate

            if len(audio.shape) == 1:
                channels = 1
            else:
                channels = audio.shape[1]

            filename = os.path.basename(file_path)

            self.info.setText(
                f"""
File: {filename}

Sample Rate: {sample_rate} Hz

Channels: {channels}

Duration: {duration:.2f} seconds

Status: Audio loaded successfully
"""
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"Could not load audio:\n{e}"
            )


app = QApplication(sys.argv)

window = AudioSystem()
window.show()

sys.exit(app.exec())
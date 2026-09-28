import os
import sys
from pathlib import Path

# ==========================================================
# NUMERICAL LIBRARY THREAD LIMIT
# ==========================================================

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"


# ==========================================================
# PROJECT ROOT
# ==========================================================

PROJECT_ROOT = (
    Path(__file__).resolve().parent.parent
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )


# ==========================================================
# QT IMPORTS
# ==========================================================

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QProgressBar,
    QScrollArea,
    QGroupBox
)


# ==========================================================
# PROJECT MODULES
# ==========================================================

from gui_pipeline import analyze_audio_for_gui

from audio.player import AudioPlayer

from audio.event_player import EventPlayer

from gui.radar import RadarWidget

from gui.waveform import WaveformWidget


# ==========================================================
# MAIN GUI
# ==========================================================

class AudioSystemGUI(QWidget):

    def __init__(self):

        super().__init__()

        # --------------------------------------------------
        # DATA
        # --------------------------------------------------

        self.selected_file = None

        self.results = []

        self.adaptive_audio = None

        self.spatial_audio = None

        # --------------------------------------------------
        # AUDIO PLAYERS
        # --------------------------------------------------

        self.player = AudioPlayer()

        self.event_player = EventPlayer()

        # --------------------------------------------------
        # PROCESSING STATUS
        # --------------------------------------------------

        self.status_steps = [
            "Audio Loaded",
            "AI Sound Detection",
            "Decision Engine",
            "Priority Engine",
            "GCC-PHAT Localization",
            "Adaptive DSP",
            "3D Spatial Rendering"
        ]

        # --------------------------------------------------
        # WINDOW
        # --------------------------------------------------

        self.setWindowTitle(
            "AI 3D Situational Audio System"
        )

        self.setMinimumSize(
            1200,
            750
        )

        self.resize(
            1350,
            850
        )

        # --------------------------------------------------
        # BUILD UI
        # --------------------------------------------------

        self.build_ui()

    # ======================================================
    # STYLES
    # ======================================================

    def apply_styles(self):

        self.setStyleSheet("""
            QWidget {
                font-family: Arial;
                font-size: 13px;
            }

            QGroupBox {
                border: 1px solid #555555;
                border-radius: 8px;
                margin-top: 12px;
                padding: 10px;
                font-weight: bold;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 5px;
            }

            QPushButton {
                min-height: 36px;
                padding: 5px 14px;
                border: 1px solid #555555;
                border-radius: 6px;
            }

            QPushButton:hover {
                border: 1px solid #888888;
            }

            QTableWidget {
                border: 1px solid #555555;
                border-radius: 6px;
                gridline-color: #444444;
            }

            QHeaderView::section {
                padding: 7px;
                font-weight: bold;
            }

            QProgressBar {
                min-height: 20px;
                border: 1px solid #555555;
                border-radius: 5px;
                text-align: center;
            }
        """)

    # ======================================================
    # BUILD UI
    # ======================================================

    def build_ui(self):

        self.apply_styles()

        root_layout = QVBoxLayout()

        root_layout.setContentsMargins(
            15,
            15,
            15,
            15
        )

        root_layout.setSpacing(
            12
        )

        # --------------------------------------------------
        # SCROLL AREA
        # --------------------------------------------------

        scroll_area = QScrollArea()

        scroll_area.setWidgetResizable(
            True
        )

        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        content = QWidget()

        content_layout = QVBoxLayout()

        content_layout.setContentsMargins(
            5,
            5,
            5,
            20
        )

        content_layout.setSpacing(
            14
        )

        # ==================================================
        # HEADER
        # ==================================================

        header = QFrame()

        header_layout = QVBoxLayout()

        title = QLabel(
            "AUDIO SYSTEM" \
            ""
        )

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        subtitle = QLabel(
            "AI-Based Adaptive Acoustic Awareness"
        )

        subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        subtitle.setStyleSheet("""
            font-size: 14px;
        """)

        header_layout.addWidget(
            title
        )

        header_layout.addWidget(
            subtitle
        )

        header.setLayout(
            header_layout
        )

        content_layout.addWidget(
            header
        )

        # ==================================================
        # AUDIO INPUT
        # ==================================================

        input_group = QGroupBox(
            "Audio Input"
        )

        input_layout = QHBoxLayout()

        self.file_label = QLabel(
            "No audio file selected"
        )

        self.file_label.setMinimumHeight(
            34
        )

        self.file_label.setStyleSheet("""
            padding: 7px;
            border: 1px solid #555555;
            border-radius: 6px;
        """)

        self.upload_button = QPushButton(
            "📁 Upload Mixed Audio"
        )

        self.upload_button.clicked.connect(
            self.select_audio
        )

        self.analyze_button = QPushButton(
            "⚡ Analyze"
        )

        self.analyze_button.clicked.connect(
            self.analyze_audio
        )

        input_layout.addWidget(
            self.file_label,
            4
        )

        input_layout.addWidget(
            self.upload_button,
            1
        )

        input_layout.addWidget(
            self.analyze_button,
            1
        )

        input_group.setLayout(
            input_layout
        )

        content_layout.addWidget(
            input_group
        )

        # ==================================================
        # SYSTEM PROCESSING STATUS
        # ==================================================

        status_group = QGroupBox(
            "System Processing Status"
        )

        status_layout = QGridLayout()

        self.status_labels = []

        for index, step in enumerate(
            self.status_steps
        ):

            label = QLabel(
                f"○ {step}"
            )

            label.setMinimumHeight(
                22
            )

            self.status_labels.append(
                label
            )

            row = index // 2
            column = index % 2

            status_layout.addWidget(
                label,
                row,
                column
            )

        self.progress_bar = QProgressBar()

        self.progress_bar.setRange(
            0,
            100
        )

        self.progress_bar.setValue(
            0
        )

        status_layout.addWidget(
            self.progress_bar,
            4,
            0,
            1,
            2
        )

        self.status_label = QLabel(
            "System Ready"
        )

        self.status_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        status_layout.addWidget(
            self.status_label,
            5,
            0,
            1,
            2
        )

        status_group.setLayout(
            status_layout
        )

        content_layout.addWidget(
            status_group
        )

        # ==================================================
        # PROCESSING MODULES
        # ==================================================

        module_group = QGroupBox(
            "Processing Modules"
        )

        module_layout = QGridLayout()

        module_names = [
            "AI MODEL",
            "DECISION",
            "PRIORITY",
            "DSP",
            "GCC-PHAT",
            "3D AUDIO"
        ]

        for index, module in enumerate(
            module_names
        ):

            label = QLabel(
                f"● {module}"
            )

            label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            label.setMinimumHeight(
                32
            )

            label.setStyleSheet("""
                border: 1px solid #555555;
                border-radius: 6px;
                font-weight: bold;
            """)

            row = index // 3
            column = index % 3

            module_layout.addWidget(
                label,
                row,
                column
            )

        module_group.setLayout(
            module_layout
        )

        content_layout.addWidget(
            module_group
        )

        # ==================================================
        # WAVEFORM + RADAR
        # ==================================================

        visualization_layout = QHBoxLayout()

        visualization_layout.setSpacing(
            14
        )

        # --------------------------------------------------
        # WAVEFORM
        # --------------------------------------------------

        waveform_group = QGroupBox(
            "📊 Audio Waveform & Event Timeline"
        )

        waveform_layout = QVBoxLayout()

        self.waveform = WaveformWidget()

        self.waveform.setMinimumHeight(
            270
        )

        self.waveform.setMaximumHeight(
            320
        )

        waveform_layout.addWidget(
            self.waveform
        )

        waveform_group.setLayout(
            waveform_layout
        )

        # --------------------------------------------------
        # RADAR
        # --------------------------------------------------

        radar_group = QGroupBox(
            "🎯 Acoustic Direction Radar"
        )

        radar_layout = QVBoxLayout()

        self.radar = RadarWidget()

        self.radar.setMinimumHeight(
            270
        )

        self.radar.setMaximumHeight(
            320
        )

        radar_layout.addWidget(
            self.radar
        )

        radar_group.setLayout(
            radar_layout
        )

        visualization_layout.addWidget(
            waveform_group,
            1
        )

        visualization_layout.addWidget(
            radar_group,
            1
        )

        content_layout.addLayout(
            visualization_layout
        )

        # ==================================================
        # EVENT TABLE
        # ==================================================

        event_group = QGroupBox(
            "🔊 Detected Acoustic Events"
        )

        event_layout = QVBoxLayout()

        self.event_table = QTableWidget()

        self.event_table.setColumnCount(
            7
        )

        self.event_table.setHorizontalHeaderLabels(
            [
                "Time",
                "Sound",
                "Confidence",
                "Priority",
                "Action",
                "Angle",
                "Direction"
            ]
        )

        self.event_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.event_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.event_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.event_table.setMinimumHeight(
            220
        )

        self.event_table.setMaximumHeight(
            320
        )

        self.event_table.cellClicked.connect(
            self.show_selected_event
        )

        event_layout.addWidget(
            self.event_table
        )

        event_group.setLayout(
            event_layout
        )

        content_layout.addWidget(
            event_group
        )

        # ==================================================
        # SELECTED EVENT
        # ==================================================

        selected_group = QGroupBox(
            "Selected Event"
        )

        selected_layout = QVBoxLayout()

        self.selected_event_label = QLabel(
            "Select an event from the table."
        )

        self.selected_event_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.selected_event_label.setWordWrap(
            True
        )

        self.selected_event_label.setMinimumHeight(
            100
        )

        selected_layout.addWidget(
            self.selected_event_label
        )

        # --------------------------------------------------
        # EVENT PLAYBACK
        # --------------------------------------------------

        selected_buttons = QHBoxLayout()

        self.play_event_button = QPushButton(
            "▶ Play Selected Event"
        )

        self.play_event_button.clicked.connect(
            self.play_selected_event
        )

        self.stop_event_button = QPushButton(
            "■ Stop Event"
        )

        self.stop_event_button.clicked.connect(
            self.stop_event
        )

        selected_buttons.addWidget(
            self.play_event_button
        )

        selected_buttons.addWidget(
            self.stop_event_button
        )

        selected_layout.addLayout(
            selected_buttons
        )

        selected_group.setLayout(
            selected_layout
        )

        content_layout.addWidget(
            selected_group
        )

        # ==================================================
        # AUDIO COMPARISON
        # ==================================================

        audio_group = QGroupBox(
            "🎧 Audio Comparison"
        )

        audio_layout = QHBoxLayout()

        self.original_button = QPushButton(
            "▶ Original Audio"
        )

        self.original_button.clicked.connect(
            self.play_original
        )

        self.enhanced_button = QPushButton(
            "▶ AI Enhanced"
        )

        self.enhanced_button.clicked.connect(
            self.play_enhanced
        )

        self.spatial_button = QPushButton(
            "▶ 3D Spatial Audio"
        )

        self.spatial_button.clicked.connect(
            self.play_spatial
        )

        self.stop_button = QPushButton(
            "■ Stop"
        )

        self.stop_button.clicked.connect(
            self.stop_audio
        )

        audio_layout.addWidget(
            self.original_button
        )

        audio_layout.addWidget(
            self.enhanced_button
        )

        audio_layout.addWidget(
            self.spatial_button
        )

        audio_layout.addWidget(
            self.stop_button
        )

        audio_group.setLayout(
            audio_layout
        )

        content_layout.addWidget(
            audio_group
        )

        # ==================================================
        # CONTENT
        # ==================================================

        content.setLayout(
            content_layout
        )

        scroll_area.setWidget(
            content
        )

        root_layout.addWidget(
            scroll_area
        )

        self.setLayout(
            root_layout
        )

    # ======================================================
    # PROCESSING STATUS
    # ======================================================

    def reset_processing_status(self):

        for index, label in enumerate(
            self.status_labels
        ):

            label.setText(
                f"○ {self.status_steps[index]}"
            )

        self.progress_bar.setValue(
            0
        )

        self.status_label.setText(
            "System Ready"
        )

    def show_processing_complete(self):

        for label, step in zip(
            self.status_labels,
            self.status_steps
        ):

            label.setText(
                f"✓ {step}"
            )

        self.progress_bar.setValue(
            100
        )

        QApplication.processEvents()

    # ======================================================
    # SELECT AUDIO
    # ======================================================

    def select_audio(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Mixed Audio",
            "",
            "WAV Audio (*.wav)"
        )

        if not file_path:
            return

        self.selected_file = Path(
            file_path
        ).resolve()

        # --------------------------------------------------
        # Reset
        # --------------------------------------------------

        self.results = []

        self.adaptive_audio = None

        self.spatial_audio = None

        # --------------------------------------------------
        # Clear event table
        # --------------------------------------------------

        self.event_table.setRowCount(
            0
        )

        # --------------------------------------------------
        # Clear radar
        # --------------------------------------------------

        self.radar.set_events(
            []
        )

        # --------------------------------------------------
        # Clear waveform events
        # --------------------------------------------------

        self.waveform.set_events(
            []
        )

        self.waveform.set_selected_event(
            None
        )

        # --------------------------------------------------
        # Load waveform
        # --------------------------------------------------

        self.waveform.load_audio(
            self.selected_file
        )

        # --------------------------------------------------
        # Display filename
        # --------------------------------------------------

        self.file_label.setText(
            self.selected_file.name
        )

        self.selected_event_label.setText(
            "Select an event from the table."
        )

        self.reset_processing_status()

        self.status_label.setText(
            "Audio file selected"
        )

    # ======================================================
    # ANALYZE
    # ======================================================

    def analyze_audio(self):

        if self.selected_file is None:

            QMessageBox.warning(
                self,
                "No Audio",
                "Please upload an audio file first."
            )

            return

        self.run_analysis(
            self.selected_file
        )

    # ======================================================
    # RUN ANALYSIS
    # ======================================================

    def run_analysis(
        self,
        audio_file
    ):

        self.reset_processing_status()

        self.results = []

        self.event_table.setRowCount(
            0
        )

        self.radar.set_events(
            []
        )

        self.waveform.set_events(
            []
        )

        self.selected_event_label.setText(
            "Processing audio..."
        )

        self.status_label.setText(
            "Starting analysis..."
        )

        # --------------------------------------------------
        # Disable input controls
        # --------------------------------------------------

        self.analyze_button.setEnabled(
            False
        )

        self.upload_button.setEnabled(
            False
        )

        # --------------------------------------------------
        # Audio loaded
        # --------------------------------------------------

        self.status_labels[0].setText(
            "✓ Audio Loaded"
        )

        self.progress_bar.setValue(
            5
        )

        QApplication.processEvents()

        try:

            result = (
                analyze_audio_for_gui(
                    audio_file
                )
            )

        except Exception as error:

            self.analyze_button.setEnabled(
                True
            )

            self.upload_button.setEnabled(
                True
            )

            self.status_label.setText(
                "Analysis failed."
            )

            self.selected_event_label.setText(
                "Analysis failed."
            )

            QMessageBox.critical(
                self,
                "Analysis Error",
                str(error)
            )

            return

        # --------------------------------------------------
        # No results
        # --------------------------------------------------

        if not result:

            self.analyze_button.setEnabled(
                True
            )

            self.upload_button.setEnabled(
                True
            )

            self.status_label.setText(
                "No confident events detected."
            )

            self.selected_event_label.setText(
                "No confident events detected."
            )

            return

        # --------------------------------------------------
        # Store results
        # --------------------------------------------------

        self.results = result[
            "events"
        ]

        self.adaptive_audio = Path(
            result[
                "adaptive_audio"
            ]
        )

        self.spatial_audio = Path(
            result[
                "spatial_audio"
            ]
        )

        # --------------------------------------------------
        # Complete status
        # --------------------------------------------------

        self.show_processing_complete()

        # --------------------------------------------------
        # Update event table
        # --------------------------------------------------

        self.populate_table()

        # --------------------------------------------------
        # Update radar
        # --------------------------------------------------

        self.radar.set_events(
            self.results
        )

        # --------------------------------------------------
        # Update waveform
        # --------------------------------------------------

        self.waveform.set_events(
            self.results
        )

        # --------------------------------------------------
        # Selected event message
        # --------------------------------------------------

        self.selected_event_label.setText(
            "Select an event from the table "
            "to inspect its details."
        )

        # --------------------------------------------------
        # Complete
        # --------------------------------------------------

        self.status_label.setText(
            f"✓ Analysis complete — "
            f"{len(self.results)} events detected."
        )

        self.analyze_button.setEnabled(
            True
        )

        self.upload_button.setEnabled(
            True
        )

    # ======================================================
    # EVENT TABLE
    # ======================================================

    def populate_table(self):

        self.event_table.setRowCount(
            len(self.results)
        )

        for row, event in enumerate(
            self.results
        ):

            values = [

                (
                    f"{event['start']:.2f} - "
                    f"{event['end']:.2f}s"
                ),

                event["label"],

                (
                    f"{event['confidence'] * 100:.1f}%"
                ),

                event["priority"],

                event["action"],

                (
                    f"{event['angle']:.1f}°"
                ),

                event["direction"]
            ]

            for column, value in enumerate(
                values
            ):

                item = QTableWidgetItem(
                    str(value)
                )

                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                self.event_table.setItem(
                    row,
                    column,
                    item
                )

    # ======================================================
    # EVENT SELECTION
    # ======================================================

    def show_selected_event(
        self,
        row,
        column
    ):

        if row < 0:
            return

        if row >= len(
            self.results
        ):
            return

        event = self.results[row]

        # Radar highlight
        self.radar.set_selected_event(
            row
        )

        # Waveform highlight
        self.waveform.set_selected_event(
            row
        )

        # Event details
        self.selected_event_label.setText(
            f"""
🔊 Sound: {event['label']}

Confidence: {event['confidence'] * 100:.1f}%

Priority: {event['priority']}

Action: {event['action']}

Angle: {event['angle']:.1f}°

Direction: {event['direction']}

Time: {event['start']:.2f}s – {event['end']:.2f}s
"""
        )

        self.status_label.setText(
            f"Selected: {event['label']}"
        )

    # ======================================================
    # PLAY SELECTED EVENT
    # ======================================================

    def play_selected_event(self):

        if self.selected_file is None:
            return

        selected_rows = (
            self.event_table
            .selectionModel()
            .selectedRows()
        )

        if not selected_rows:

            QMessageBox.warning(
                self,
                "No Event",
                "Please select an event first."
            )

            return

        row = selected_rows[0].row()

        if row >= len(
            self.results
        ):
            return

        event = self.results[row]

        try:

            self.event_player.play_event(
                self.selected_file,
                event["start"],
                event["end"]
            )

            self.status_label.setText(
                f"▶ Playing {event['label']} event..."
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Event Playback Error",
                str(error)
            )

    # ======================================================
    # STOP EVENT
    # ======================================================

    def stop_event(self):

        self.event_player.stop()

        self.status_label.setText(
            "Event playback stopped."
        )

    # ======================================================
    # ORIGINAL AUDIO
    # ======================================================

    def play_original(self):

        if self.selected_file is None:
            return

        try:

            self.player.play(
                self.selected_file
            )

            self.status_label.setText(
                "▶ Playing original audio..."
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Playback Error",
                str(error)
            )

    # ======================================================
    # ENHANCED AUDIO
    # ======================================================

    def play_enhanced(self):

        if self.adaptive_audio is None:

            QMessageBox.warning(
                self,
                "Not Processed",
                "Analyze the audio first."
            )

            return

        try:

            self.player.play(
                self.adaptive_audio
            )

            self.status_label.setText(
                "▶ Playing AI enhanced audio..."
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Playback Error",
                str(error)
            )

    # ======================================================
    # 3D SPATIAL AUDIO
    # ======================================================

    def play_spatial(self):

        if self.spatial_audio is None:

            QMessageBox.warning(
                self,
                "Not Processed",
                "Analyze the audio first."
            )

            return

        try:

            self.player.play(
                self.spatial_audio
            )

            self.status_label.setText(
                "▶ Playing 3D spatial audio..."
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Playback Error",
                str(error)
            )

    # ======================================================
    # STOP ALL AUDIO
    # ======================================================

    def stop_audio(self):

        self.player.stop()

        self.event_player.stop()

        self.status_label.setText(
            "Audio playback stopped."
        )


# ==========================================================
# START APPLICATION
# ==========================================================

if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    window = AudioSystemGUI()

    window.show()

    sys.exit(
        app.exec()
    )
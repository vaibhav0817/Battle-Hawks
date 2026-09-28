from pathlib import Path

import numpy as np
import soundfile as sf

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QPainter,
    QPen,
    QBrush,
    QColor
)
from PySide6.QtWidgets import QWidget


class WaveformWidget(QWidget):

    def __init__(self):

        super().__init__()

        self.audio_file = None
        self.events = []
        self.selected_index = None

        self.samples = None
        self.sample_rate = None

        self.duration = 0.0

        self.setMinimumHeight(260)

    # ======================================================
    # LOAD AUDIO
    # ======================================================

    def load_audio(self, audio_file):

        self.audio_file = Path(
            audio_file
        ).resolve()

        try:

            audio, self.sample_rate = sf.read(
                str(self.audio_file),
                always_2d=True
            )

            # Convert stereo to mono for visualization
            mono = np.mean(
                audio,
                axis=1
            )

            self.samples = mono.astype(
                np.float32
            )

            self.duration = (
                len(self.samples)
                / self.sample_rate
            )

        except Exception:

            self.samples = None
            self.sample_rate = None
            self.duration = 0.0

        self.update()

    # ======================================================
    # SET EVENTS
    # ======================================================

    def set_events(self, events):

        self.events = list(events)

        self.update()

    # ======================================================
    # SELECT EVENT
    # ======================================================

    def set_selected_event(self, index):

        if index is None:

            self.selected_index = None

        elif 0 <= index < len(self.events):

            self.selected_index = index

        else:

            self.selected_index = None

        self.update()

    # ======================================================
    # PAINT
    # ======================================================

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        width = self.width()
        height = self.height()

        # --------------------------------------------------
        # Background
        # --------------------------------------------------

        painter.fillRect(
            self.rect(),
            self.palette().window()
        )

        # --------------------------------------------------
        # No audio
        # --------------------------------------------------

        if (
            self.samples is None
            or len(self.samples) == 0
            or self.duration <= 0
        ):

            painter.setPen(
                QPen(
                    QColor(150, 150, 150)
                )
            )

            painter.drawText(
                width // 2 - 60,
                height // 2,
                "No audio loaded"
            )

            painter.end()

            return

        # ==================================================
        # WAVEFORM AREA
        # ==================================================

        left_margin = 20
        right_margin = 20

        top_margin = 55
        bottom_margin = 35

        plot_width = (
            width
            - left_margin
            - right_margin
        )

        plot_height = (
            height
            - top_margin
            - bottom_margin
        )

        center_y = (
            top_margin
            + plot_height / 2
        )

        amplitude = (
            plot_height * 0.42
        )

        # ==================================================
        # EVENT REGIONS
        # ==================================================

        for index, event_data in enumerate(
            self.events
        ):

            start = float(
                event_data.get(
                    "start",
                    0.0
                )
            )

            end = float(
                event_data.get(
                    "end",
                    0.0
                )
            )

            start = max(
                0.0,
                min(
                    self.duration,
                    start
                )
            )

            end = max(
                0.0,
                min(
                    self.duration,
                    end
                )
            )

            if end <= start:
                continue

            x1 = (
                left_margin
                + (start / self.duration)
                * plot_width
            )

            x2 = (
                left_margin
                + (end / self.duration)
                * plot_width
            )

            # ----------------------------------------------
            # Selected region
            # ----------------------------------------------

            if index == self.selected_index:

                fill_color = QColor(
                    255,
                    80,
                    80,
                    70
                )

            else:

                fill_color = QColor(
                    120,
                    120,
                    120,
                    35
                )

            painter.setBrush(
                QBrush(
                    fill_color
                )
            )

            painter.setPen(
                Qt.PenStyle.NoPen
            )

            painter.drawRect(
                int(x1),
                int(top_margin),
                max(
                    2,
                    int(x2 - x1)
                ),
                int(plot_height)
            )

        # ==================================================
        # CENTER LINE
        # ==================================================

        painter.setPen(
            QPen(
                QColor(90, 90, 90)
            )
        )

        painter.drawLine(
            int(left_margin),
            int(center_y),
            int(width - right_margin),
            int(center_y)
        )

        # ==================================================
        # WAVEFORM
        # ==================================================

        painter.setPen(
            QPen(
                QColor(180, 180, 180)
            )
        )

        total_samples = len(
            self.samples
        )

        pixels = max(
            1,
            int(plot_width)
        )

        samples_per_pixel = (
            total_samples
            / pixels
        )

        for x in range(pixels):

            start_index = int(
                x
                * samples_per_pixel
            )

            end_index = int(
                (x + 1)
                * samples_per_pixel
            )

            end_index = min(
                total_samples,
                max(
                    start_index + 1,
                    end_index
                )
            )

            segment = self.samples[
                start_index:end_index
            ]

            if len(segment) == 0:
                continue

            min_value = float(
                np.min(segment)
            )

            max_value = float(
                np.max(segment)
            )

            y1 = (
                center_y
                - max_value * amplitude
            )

            y2 = (
                center_y
                - min_value * amplitude
            )

            painter.drawLine(
                int(left_margin + x),
                int(y1),
                int(left_margin + x),
                int(y2)
            )

        # ==================================================
        # EVENT LABELS
        # ==================================================

        for index, event_data in enumerate(
            self.events
        ):

            start = float(
                event_data.get(
                    "start",
                    0.0
                )
            )

            end = float(
                event_data.get(
                    "end",
                    0.0
                )
            )

            label = event_data.get(
                "label",
                "Unknown"
            )

            x = (
                left_margin
                + (
                    (
                        start + end
                    ) / 2
                    / self.duration
                )
                * plot_width
            )

            if index == self.selected_index:

                painter.setPen(
                    QPen(
                        QColor(255, 255, 255)
                    )
                )

            else:

                painter.setPen(
                    QPen(
                        QColor(210, 210, 210)
                    )
                )

            painter.drawText(
                int(x - 35),
                int(top_margin - 12),
                label[:14]
            )

        # ==================================================
        # TIME LABELS
        # ==================================================

        painter.setPen(
            QPen(
                QColor(160, 160, 160)
            )
        )

        tick_count = 5

        for i in range(
            tick_count + 1
        ):

            ratio = (
                i / tick_count
            )

            x = (
                left_margin
                + ratio
                * plot_width
            )

            time_value = (
                ratio
                * self.duration
            )

            painter.drawLine(
                int(x),
                int(height - bottom_margin + 2),
                int(x),
                int(height - bottom_margin + 8)
            )

            painter.drawText(
                int(x - 12),
                int(height - 10),
                f"{time_value:.0f}s"
            )

        # ==================================================
        # TITLE
        # ==================================================

        painter.setPen(
            QPen(
                QColor(220, 220, 220)
            )
        )

        painter.drawText(
            20,
            20,
            "Audio Waveform & Event Timeline"
        )

        # ==================================================
        # FOOTER
        # ==================================================

        painter.setPen(
            QPen(
                QColor(130, 130, 130)
            )
        )

        painter.drawText(
            20,
            height - 10,
            f"Duration: {self.duration:.2f}s"
        )

        painter.end()
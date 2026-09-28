import math

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import (
    QPainter,
    QPen,
    QBrush,
    QColor,
    QFont
)
from PySide6.QtWidgets import QWidget


class RadarWidget(QWidget):

    def __init__(self):

        super().__init__()

        # All detected events
        self.events = []

        # Selected table row
        self.selected_index = None

        self.setMinimumHeight(
            380
        )

    # ======================================================
    # SET EVENTS
    # ======================================================

    def set_events(self, events):

        self.events = list(events)

        self.selected_index = None

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
    # PAINT RADAR
    # ======================================================

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        width = self.width()
        height = self.height()

        center_x = width / 2
        center_y = height / 2

        radius = min(
            width,
            height
        ) * 0.32

        # ==================================================
        # BACKGROUND
        # ==================================================

        painter.fillRect(
            self.rect(),
            self.palette().window()
        )

        # ==================================================
        # RADAR RINGS
        # ==================================================

        ring_pen = QPen(
            QColor(
                90,
                90,
                90
            )
        )

        ring_pen.setWidth(
            1
        )

        painter.setPen(
            ring_pen
        )

        for factor in [
            1.0,
            0.78,
            0.56,
            0.34
        ]:

            r = radius * factor

            painter.drawEllipse(
                QPointF(
                    center_x,
                    center_y
                ),
                r,
                r
            )

        # ==================================================
        # CROSS LINES
        # ==================================================

        painter.drawLine(
            QPointF(
                center_x - radius,
                center_y
            ),
            QPointF(
                center_x + radius,
                center_y
            )
        )

        painter.drawLine(
            QPointF(
                center_x,
                center_y - radius
            ),
            QPointF(
                center_x,
                center_y + radius
            )
        )

        # ==================================================
        # DIRECTION LABELS
        # ==================================================

        painter.setPen(
            QPen(
                QColor(
                    220,
                    220,
                    220
                )
            )
        )

        font = QFont()

        font.setBold(
            True
        )

        font.setPointSize(
            10
        )

        painter.setFont(
            font
        )

        painter.drawText(
            int(
                center_x - 25
            ),
            int(
                center_y - radius - 15
            ),
            "FRONT"
        )

        painter.drawText(
            int(
                center_x + radius + 12
            ),
            int(
                center_y + 5
            ),
            "RIGHT"
        )

        painter.drawText(
            int(
                center_x - radius - 45
            ),
            int(
                center_y + 5
            ),
            "LEFT"
        )

        painter.drawText(
            int(
                center_x - 22
            ),
            int(
                center_y + radius + 25
            ),
            "REAR*"
        )

        # ==================================================
        # SOLDIER CENTER
        # ==================================================

        painter.setBrush(
            QBrush(
                QColor(
                    230,
                    230,
                    230
                )
            )
        )

        painter.setPen(
            QPen(
                QColor(
                    230,
                    230,
                    230
                )
            )
        )

        painter.drawEllipse(
            QPointF(
                center_x,
                center_y
            ),
            9,
            9
        )

        painter.setPen(
            QPen(
                QColor(
                    190,
                    190,
                    190
                )
            )
        )

        painter.drawText(
            int(
                center_x + 14
            ),
            int(
                center_y + 5
            ),
            "SOLDIER"
        )

        # ==================================================
        # NO EVENTS
        # ==================================================

        if not self.events:

            painter.setPen(
                QPen(
                    QColor(
                        150,
                        150,
                        150
                    )
                )
            )

            painter.drawText(
                int(
                    center_x - 60
                ),
                int(
                    center_y + 80
                ),
                "No events detected"
            )

            painter.end()

            return

        # ==================================================
        # COUNT EVENTS AT SAME ANGLE
        #
        # IMPORTANT:
        # We NEVER modify the actual angle.
        # Only radius is changed to avoid overlap.
        # ==================================================

        angle_positions = {}

        for index, event_data in enumerate(
            self.events
        ):

            angle = float(
                event_data.get(
                    "angle",
                    0.0
                )
            )

            angle = max(
                -90.0,
                min(
                    90.0,
                    angle
                )
            )

            angle_key = round(
                angle,
                1
            )

            if angle_key not in angle_positions:

                angle_positions[
                    angle_key
                ] = []

            angle_positions[
                angle_key
            ].append(index)

        # ==================================================
        # DRAW EVENTS
        # ==================================================

        for event_index, event_data in enumerate(
            self.events
        ):

            # --------------------------------------------------
            # ORIGINAL ANGLE
            # --------------------------------------------------

            angle = float(
                event_data.get(
                    "angle",
                    0.0
                )
            )

            angle = max(
                -90.0,
                min(
                    90.0,
                    angle
                )
            )

            confidence = float(
                event_data.get(
                    "confidence",
                    0.0
                )
            )

            label = event_data.get(
                "label",
                "Unknown"
            )

            priority = event_data.get(
                "priority",
                "UNKNOWN"
            )

            # --------------------------------------------------
            # Determine position among same-angle events
            # --------------------------------------------------

            angle_key = round(
                angle,
                1
            )

            same_angle_events = (
                angle_positions[
                    angle_key
                ]
            )

            same_angle_index = (
                same_angle_events.index(
                    event_index
                )
            )

            # --------------------------------------------------
            # IMPORTANT:
            # Keep ANGLE EXACTLY unchanged.
            #
            # Only move radius slightly.
            # --------------------------------------------------

            radius_offset = (
                same_angle_index
                * 25
            )

            event_radius = (
                radius
                - radius_offset
            )

            minimum_radius = (
                radius * 0.55
            )

            event_radius = max(
                minimum_radius,
                event_radius
            )

            # --------------------------------------------------
            # Confidence affects radial distance,
            # but NOT angle.
            # --------------------------------------------------

            confidence_factor = (
                0.75
                + min(
                    confidence,
                    1.0
                ) * 0.25
            )

            event_radius *= (
                confidence_factor
            )

            # --------------------------------------------------
            # ANGLE → RADAR POSITION
            #
            # Positive angle = RIGHT
            # Negative angle = LEFT
            # --------------------------------------------------

            radians = math.radians(
                angle
            )

            point_x = (
                center_x
                + math.sin(
                    radians
                ) * event_radius
            )

            point_y = (
                center_y
                - math.cos(
                    radians
                ) * event_radius
            )

            # ==================================================
            # PRIORITY COLOR
            # ==================================================

            if priority == "CRITICAL":

                base_color = QColor(
                    255,
                    80,
                    80
                )

            elif priority == "IMPORTANT":

                base_color = QColor(
                    255,
                    190,
                    70
                )

            elif priority == "BACKGROUND":

                base_color = QColor(
                    120,
                    180,
                    255
                )

            else:

                base_color = QColor(
                    160,
                    160,
                    160
                )

            # ==================================================
            # SELECTED / NON-SELECTED
            # ==================================================

            is_selected = (
                self.selected_index
                == event_index
            )

            if is_selected:

                marker_color = QColor(
                    255,
                    255,
                    255
                )

                line_color = base_color

                line_width = 4

                marker_radius = 11

                text_color = QColor(
                    255,
                    255,
                    255
                )

            else:

                if self.selected_index is not None:

                    marker_color = QColor(
                        90,
                        90,
                        90
                    )

                    line_color = QColor(
                        70,
                        70,
                        70
                    )

                    line_width = 1

                    marker_radius = 5

                    text_color = QColor(
                        120,
                        120,
                        120
                    )

                else:

                    marker_color = base_color

                    line_color = base_color

                    line_width = 2

                    marker_radius = 7

                    text_color = QColor(
                        235,
                        235,
                        235
                    )

            # ==================================================
            # DIRECTION LINE
            # ==================================================

            direction_pen = QPen(
                line_color
            )

            direction_pen.setWidth(
                line_width
            )

            painter.setPen(
                direction_pen
            )

            painter.drawLine(
                QPointF(
                    center_x,
                    center_y
                ),
                QPointF(
                    point_x,
                    point_y
                )
            )

            # ==================================================
            # SELECTED GLOW
            # ==================================================

            if is_selected:

                glow_pen = QPen(
                    QColor(
                        255,
                        255,
                        255,
                        110
                    )
                )

                glow_pen.setWidth(
                    3
                )

                painter.setPen(
                    glow_pen
                )

                painter.setBrush(
                    Qt.BrushStyle.NoBrush
                )

                painter.drawEllipse(
                    QPointF(
                        point_x,
                        point_y
                    ),
                    18,
                    18
                )

            # ==================================================
            # EVENT MARKER
            # ==================================================

            painter.setBrush(
                QBrush(
                    marker_color
                )
            )

            painter.setPen(
                QPen(
                    marker_color
                )
            )

            painter.drawEllipse(
                QPointF(
                    point_x,
                    point_y
                ),
                marker_radius,
                marker_radius
            )

            # ==================================================
            # EVENT LABEL
            # ==================================================

            painter.setPen(
                QPen(
                    text_color
                )
            )

            font = QFont()

            if is_selected:

                font.setBold(
                    True
                )

                font.setPointSize(
                    10
                )

            else:

                font.setPointSize(
                    9
                )

            painter.setFont(
                font
            )

            display_text = (
                f"{label[:18]} "
                f"({confidence * 100:.0f}%)"
            )

            if is_selected:

                display_text = (
                    f"▶ {display_text}"
                )

            painter.drawText(
                int(
                    point_x + 12
                ),
                int(
                    point_y + 4
                ),
                display_text
            )

            # ==================================================
            # ANGLE LABEL
            # ==================================================

            painter.setPen(
                QPen(
                    text_color
                )
            )

            painter.drawText(
                int(
                    point_x + 12
                ),
                int(
                    point_y + 18
                ),
                f"{angle:+.1f}°"
            )

        # ==================================================
        # LEGEND
        # ==================================================

        legend_y = int(
            height - 38
        )

        legend_items = [
            (
                QColor(
                    255,
                    80,
                    80
                ),
                "Critical"
            ),
            (
                QColor(
                    255,
                    190,
                    70
                ),
                "Important"
            ),
            (
                QColor(
                    120,
                    180,
                    255
                ),
                "Background"
            )
        ]

        legend_x = 20

        for color, text in legend_items:

            painter.setBrush(
                QBrush(
                    color
                )
            )

            painter.setPen(
                QPen(
                    color
                )
            )

            painter.drawEllipse(
                QPointF(
                    legend_x,
                    legend_y
                ),
                5,
                5
            )

            painter.setPen(
                QPen(
                    QColor(
                        210,
                        210,
                        210
                    )
                )
            )

            painter.drawText(
                legend_x + 10,
                legend_y + 4,
                text
            )

            legend_x += 110

        # ==================================================
        # FOOTNOTE
        # ==================================================

        painter.setPen(
            QPen(
                QColor(
                    130,
                    130,
                    130
                )
            )
        )

        painter.drawText(
            20,
            height - 10,
            "* Rear direction is not validated in the current 2-mic prototype."
        )

        painter.end()
from pathlib import Path

from ai.classifier import detect_sounds
from priority.decision_engine import DecisionEngine
from priority.priority_engine import PriorityEngine
from localization.event_localizer import EventLocalizer


class EventAnalyzer:

    def __init__(self, audio_file):

        self.audio_file = Path(
            audio_file
        ).resolve()

        self.localizer = EventLocalizer(
            self.audio_file
        )

        self.decision_engine = DecisionEngine(
            confidence_threshold=0.20
        )

        self.priority_engine = PriorityEngine()

    def analyze(self):

        print("\n")
        print("================================================")
        print("        AI + GCC-PHAT EVENT ANALYZER")
        print("================================================")
        print()

        # --------------------------------------------------
        # STEP 1 — AI detection
        # --------------------------------------------------

        print("Running AI sound detection...\n")

        detections = detect_sounds(
            self.audio_file
        )

        if not detections:

            print("No detections found.")
            return []

        # --------------------------------------------------
        # STEP 2 — Decision Engine
        # --------------------------------------------------

        selected = (
            self.decision_engine.create_decisions(
                detections
            )
        )

        if not selected:

            print(
                "No confident relevant events found."
            )

            return []

        results = []

        # --------------------------------------------------
        # STEP 3 — Analyze every selected event
        # --------------------------------------------------

        for event in selected:

            label = event["label"]
            confidence = event["score"]

            # Priority
            priority = (
                self.priority_engine.get_priority(
                    label,
                    confidence
                )
            )

            # Localization
            try:

                location = (
                    self.localizer.localize_event(
                        event["start"],
                        event["end"]
                    )
                )

            except Exception:

                location = {
                    "tdoa": 0.0,
                    "angle": 0.0,
                    "direction": "UNKNOWN"
                }

            final_event = {

                "start": event["start"],
                "end": event["end"],

                "label": label,

                "confidence": confidence,

                "priority":
                    priority["priority"],

                "action":
                    priority["action"],

                "tdoa":
                    location["tdoa"],

                "angle":
                    location["angle"],

                "direction":
                    location["direction"]
            }

            results.append(
                final_event
            )

        # --------------------------------------------------
        # STEP 4 — Display
        # --------------------------------------------------

        print("\n================================================")
        print("              FINAL EVENT ANALYSIS")
        print("================================================\n")

        for event in results:

            print(
                f"{event['start']:05.2f}s - "
                f"{event['end']:05.2f}s"
            )

            print(
                f"  Sound      : "
                f"{event['label']}"
            )

            print(
                f"  Confidence : "
                f"{event['confidence'] * 100:.1f}%"
            )

            print(
                f"  Priority   : "
                f"{event['priority']}"
            )

            print(
                f"  Action     : "
                f"{event['action']}"
            )

            print(
                f"  TDOA       : "
                f"{event['tdoa'] * 1000:.3f} ms"
            )

            print(
                f"  Angle      : "
                f"{event['angle']:.2f}°"
            )

            print(
                f"  Direction  : "
                f"{event['direction']}"
            )

            print("----------------------------------------------")

        return results


if __name__ == "__main__":

    base_dir = (
        Path(__file__)
        .resolve()
        .parent
        .parent
    )

    audio_file = (
        base_dir
        / "test_audio"
        / "mic_test.wav"
    )

    analyzer = EventAnalyzer(
        audio_file
    )

    analyzer.analyze()
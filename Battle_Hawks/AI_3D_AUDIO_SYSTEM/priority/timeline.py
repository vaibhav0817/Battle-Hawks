from typing import List, Dict


class EventTimeline:

    def __init__(self):
        self.events = []

    def add_event(
        self,
        start: float,
        end: float,
        label: str,
        confidence: float,
        priority: str,
        action: str
    ):
        """
        Add one detected acoustic event.
        """

        self.events.append({
            "start": float(start),
            "end": float(end),
            "label": label,
            "confidence": float(confidence),
            "priority": priority,
            "action": action
        })

    def sort_events(self):
        """
        Sort events chronologically.
        """

        self.events.sort(
            key=lambda event: (
                event["start"],
                -event["confidence"]
            )
        )

    def get_events(self) -> List[Dict]:
        """
        Return sorted events.
        """

        self.sort_events()

        return self.events

    def print_timeline(self):

        self.sort_events()

        print("\n==============================================")
        print("              ACOUSTIC EVENT TIMELINE")
        print("==============================================\n")

        if not self.events:
            print("No events detected.")
            return

        for event in self.events:

            print(
                f"{event['start']:05.2f}s - "
                f"{event['end']:05.2f}s | "
                f"{event['label']:<25} | "
                f"{event['confidence'] * 100:5.1f}% | "
                f"{event['priority']:<10} | "
                f"{event['action']}"
            )


if __name__ == "__main__":

    timeline = EventTimeline()

    timeline.add_event(
        start=0.0,
        end=1.0,
        label="Machine gun",
        confidence=0.2864,
        priority="CRITICAL",
        action="PRESERVE_LIMIT"
    )

    timeline.add_event(
        start=1.0,
        end=2.0,
        label="Explosion",
        confidence=0.2143,
        priority="CRITICAL",
        action="PRESERVE_LIMIT"
    )

    timeline.add_event(
        start=0.0,
        end=1.0,
        label="Wind",
        confidence=0.35,
        priority="BACKGROUND",
        action="SUPPRESS"
    )

    timeline.print_timeline()
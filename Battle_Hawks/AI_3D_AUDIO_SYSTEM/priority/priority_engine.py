class PriorityEngine:

    def __init__(self):

        self.critical_sounds = {
            "gunshot",
            "gunshot, gunfire",
            "gunfire",
            "machine gun",
            "explosion",
            "artillery fire",
            "blast",
            "bomb",
            "weapon fire",
            "impact"
        }

        self.important_sounds = {
            "footsteps",
            "footstep",
            "speech",
            "conversation",
            "voice",
            "vehicle",
            "engine"
        }

        self.background_sounds = {
            "wind",
            "leaves",
            "rustling leaves",
            "static",
            "rain",
            "water",
            "background noise",
            "environmental noise"
        }

    def get_priority(self, label, confidence):

        label = label.lower().strip()

        # Critical acoustic event:
        # Preserve + protect, NOT aggressive amplification.
        for sound in self.critical_sounds:

            if sound in label:

                return {
                    "priority": "CRITICAL",
                    "score": 1.0,
                    "action": "PRESERVE_LIMIT"
                }

        # Important environmental information
        for sound in self.important_sounds:

            if sound in label:

                return {
                    "priority": "IMPORTANT",
                    "score": 0.7,
                    "action": "ENHANCE"
                }

        # Distracting/background sounds
        for sound in self.background_sounds:

            if sound in label:

                return {
                    "priority": "BACKGROUND",
                    "score": 0.3,
                    "action": "SUPPRESS"
                }

        # Unknown sounds should not be aggressively modified
        return {
            "priority": "UNKNOWN",
            "score": 0.5,
            "action": "PRESERVE"
        }


if __name__ == "__main__":

    engine = PriorityEngine()

    tests = [
        ("Machine gun", 0.86),
        ("Gunshot, gunfire", 0.79),
        ("Explosion", 0.91),
        ("Footsteps", 0.82),
        ("Speech", 0.75),
        ("Wind", 0.88),
        ("Leaves", 0.72),
        ("Impact", 0.80)
    ]

    print("\n==============================================")
    print("             PRIORITY ENGINE TEST")
    print("==============================================\n")

    for label, confidence in tests:

        result = engine.get_priority(
            label,
            confidence
        )

        print(
            f"{label:<25} "
            f"{confidence * 100:5.1f}%  →  "
            f"{result['priority']:<10} →  "
            f"{result['action']}"
        )
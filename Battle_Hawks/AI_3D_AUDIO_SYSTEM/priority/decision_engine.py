class DecisionEngine:

    def __init__(self, confidence_threshold=0.20):

        self.confidence_threshold = confidence_threshold

        # Relevant labels for our prototype
        self.allowed_sounds = {
            "gunshot, gunfire",
            "gunfire",
            "machine gun",
            "explosion",
            "artillery fire",
            "footsteps",
            "footstep",
            "speech",
            "voice",
            "conversation",
            "vehicle",
            "engine",
            "wind noise (microphone)",
            "wind",
            "leaves"
        }

    def normalize_label(self, label):
        return label.lower().strip()

    def filter_detections(self, detections):

        filtered = []

        for detection in detections:

            label = self.normalize_label(
                detection["label"]
            )

            score = detection["score"]

            # Confidence filter
            if score < self.confidence_threshold:
                continue

            # Relevant-label filter
            if label not in self.allowed_sounds:
                continue

            filtered.append(detection)

        return filtered

    def create_decisions(self, detections):

        filtered = self.filter_detections(
            detections
        )

        # ----------------------------------------------
        # Group detections by time window
        # ----------------------------------------------

        groups = {}

        for detection in filtered:

            key = (
                round(detection["start"], 2),
                round(detection["end"], 2)
            )

            if key not in groups:
                groups[key] = []

            groups[key].append(detection)

        decisions = []

        # ----------------------------------------------
        # Select ONE strongest relevant event per window
        # ----------------------------------------------

        for _, group in groups.items():

            best = max(
                group,
                key=lambda x: x["score"]
            )

            decisions.append(best.copy())

        # ----------------------------------------------
        # Sort chronologically
        # ----------------------------------------------

        decisions.sort(
            key=lambda x: x["start"]
        )

        return decisions


if __name__ == "__main__":

    engine = DecisionEngine()

    test_data = [

        {
            "start": 0.0,
            "end": 1.0,
            "label": "Gunshot, gunfire",
            "score": 0.4954
        },

        {
            "start": 0.0,
            "end": 1.0,
            "label": "Artillery fire",
            "score": 0.0848
        },

        {
            "start": 0.0,
            "end": 1.0,
            "label": "Machine gun",
            "score": 0.0390
        },

        {
            "start": 1.0,
            "end": 2.0,
            "label": "Explosion",
            "score": 0.2143
        },

        {
            "start": 1.0,
            "end": 2.0,
            "label": "Vehicle",
            "score": 0.0439
        }
    ]

    results = engine.create_decisions(
        test_data
    )

    print("\n==============================================")
    print("        FILTERED DECISION ENGINE")
    print("==============================================\n")

    for result in results:

        print(
            f"{result['start']:05.2f}s - "
            f"{result['end']:05.2f}s | "
            f"{result['label']:<25} | "
            f"{result['score'] * 100:5.1f}%"
        )
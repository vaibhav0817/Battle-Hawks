from typing import List, Dict


def merge_events(
    events: List[Dict],
    overlap_tolerance: float = 0.25
) -> List[Dict]:
    """
    Merge overlapping detections of the same sound.

    Example:
        0.0 - 1.0 Machine gun
        0.5 - 1.5 Machine gun

    becomes:

        0.0 - 1.5 Machine gun
    """

    if not events:
        return []

    # Sort by label and start time
    sorted_events = sorted(
        events,
        key=lambda x: (
            x["label"].lower(),
            x["start"]
        )
    )

    merged = []

    for event in sorted_events:

        if not merged:
            merged.append(event.copy())
            continue

        previous = merged[-1]

        same_label = (
            previous["label"].lower()
            == event["label"].lower()
        )

        overlapping = (
            event["start"]
            <= previous["end"] + overlap_tolerance
        )

        if same_label and overlapping:

            # Extend the previous event
            previous["end"] = max(
                previous["end"],
                event["end"]
            )

            # Keep highest confidence
            previous["score"] = max(
                previous["score"],
                event["score"]
            )

        else:

            merged.append(event.copy())

    # Sort back chronologically
    merged.sort(
        key=lambda x: x["start"]
    )

    return merged


if __name__ == "__main__":

    test_events = [

        {
            "start": 0.0,
            "end": 1.0,
            "label": "Machine gun",
            "score": 0.2864
        },

        {
            "start": 0.5,
            "end": 1.5,
            "label": "Machine gun",
            "score": 0.2647
        },

        {
            "start": 1.0,
            "end": 2.0,
            "label": "Explosion",
            "score": 0.2143
        }
    ]

    result = merge_events(test_events)

    print("\n==============================================")
    print("             EVENT MERGER TEST")
    print("==============================================\n")

    for event in result:

        print(
            f"{event['start']:05.2f}s - "
            f"{event['end']:05.2f}s | "
            f"{event['label']:<20} | "
            f"{event['score'] * 100:5.1f}%"
        )
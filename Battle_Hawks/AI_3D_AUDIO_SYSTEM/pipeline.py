from pathlib import Path

import numpy as np
import soundfile as sf

from ai.classifier import detect_sounds
from priority.decision_engine import DecisionEngine
from priority.priority_engine import PriorityEngine
from priority.event_merger import merge_events
from priority.timeline import EventTimeline
from localization.smart_localizer import SmartLocalizer
from audio.dsp import process_audio_file
from spatial.hrtf import HRTFRenderer


def run_pipeline(input_file):

    input_file = Path(input_file).resolve()

    base_dir = Path(__file__).resolve().parent

    adaptive_output = (
        base_dir
        / "output"
        / "adaptive_processed.wav"
    )

    final_output = (
        base_dir
        / "output"
        / "final_3d_audio.wav"
    )

    print("\n================================================")
    print("       AI 3D SITUATIONAL AUDIO SYSTEM")
    print("================================================\n")

    print(f"Input Audio : {input_file}\n")

    # ======================================================
    # 1. AI SOUND DETECTION
    # ======================================================

    print("STEP 1: AI SOUND DETECTION")
    print("-----------------------------------------------")

    detections = detect_sounds(input_file)

    if not detections:
        print("No sounds detected.")
        return

    # ======================================================
    # 2. DECISION ENGINE
    # ======================================================

    print("\nSTEP 2: DECISION ENGINE")
    print("-----------------------------------------------")

    decision_engine = DecisionEngine(
        confidence_threshold=0.20
    )

    selected_events = (
        decision_engine.create_decisions(
            detections
        )
    )

    if not selected_events:
        print("No confident events found.")
        return

    # ======================================================
    # 3. PRIORITY ENGINE
    # ======================================================

    print("\nSTEP 3: PRIORITY ENGINE")
    print("-----------------------------------------------")

    priority_engine = PriorityEngine()

    priority_events = []

    for event in selected_events:

        priority = (
            priority_engine.get_priority(
                event["label"],
                event["score"]
            )
        )

        priority_event = {
            "start": event["start"],
            "end": event["end"],
            "label": event["label"],
            "score": event["score"],
            "priority": priority["priority"],
            "action": priority["action"]
        }

        priority_events.append(
            priority_event
        )

        print(
            f"{event['start']:05.2f}s - "
            f"{event['end']:05.2f}s | "
            f"{event['label']:<25} | "
            f"{event['score'] * 100:5.1f}% | "
            f"{priority['priority']:<10}"
        )

    # ======================================================
    # 4. EVENT MERGING
    # ======================================================

    print("\nSTEP 4: EVENT MERGING")
    print("-----------------------------------------------")

    merged_events = merge_events(
        priority_events
    )

    # ======================================================
    # 5. TIMELINE
    # ======================================================

    print("\nSTEP 5: EVENT TIMELINE")
    print("-----------------------------------------------")

    timeline = EventTimeline()

    for event in merged_events:

        timeline.add_event(
            start=event["start"],
            end=event["end"],
            label=event["label"],
            confidence=event["score"],
            priority=event["priority"],
            action=event["action"]
        )

    timeline.print_timeline()

    # ======================================================
    # 6. ADAPTIVE DSP
    # ======================================================

    print("\nSTEP 6: ADAPTIVE DSP")
    print("-----------------------------------------------")

    dsp_actions = []

    for event in merged_events:

        dsp_actions.append({
            "start": event["start"],
            "end": event["end"],
            "action": event["action"]
        })

    process_audio_file(
        input_file,
        adaptive_output,
        dsp_actions
    )

    # ======================================================
    # 7. SMART LOCALIZATION
    # ======================================================

    print("\nSTEP 7: SMART LOCALIZATION")
    print("-----------------------------------------------")

    localizer = SmartLocalizer(
        input_file,
        window_ms=250
    )

    localized_events = []

    for event in merged_events:

        try:

            location = localizer.localize_event(
                event["start"],
                event["end"]
            )

            localized = event.copy()

            localized.update(location)

            localized_events.append(
                localized
            )

            print(
                f"{event['label']:<25} | "
                f"{location['angle']:7.2f}° | "
                f"{location['direction']} | "
                f"Analysis: "
                f"{location['analysis_start']:.3f}-"
                f"{location['analysis_end']:.3f}s"
            )

        except Exception as error:

            print(
                f"Localization failed for "
                f"{event['label']}: {error}"
            )

    # ======================================================
    # 8. SPATIAL AUDIO
    # ======================================================

    print("\nSTEP 8: SPATIAL AUDIO")
    print("-----------------------------------------------")

    audio, sample_rate = sf.read(
        str(adaptive_output),
        always_2d=True
    )

    mono = np.mean(
        audio,
        axis=1
    ).astype(np.float32)

    final_left = np.zeros(
        len(mono),
        dtype=np.float32
    )

    final_right = np.zeros(
        len(mono),
        dtype=np.float32
    )

    event_mask = np.zeros(
        len(mono),
        dtype=bool
    )

    renderer = HRTFRenderer(
        sample_rate
    )

    for event in localized_events:

        start_sample = int(
            event["start"] * sample_rate
        )

        end_sample = int(
            event["end"] * sample_rate
        )

        start_sample = max(
            0,
            start_sample
        )

        end_sample = min(
            len(mono),
            end_sample
        )

        if start_sample >= end_sample:
            continue

        segment = mono[
            start_sample:end_sample
        ]

        spatial = renderer.render(
            segment,
            event["angle"]
        )

        segment_length = (
            end_sample - start_sample
        )

        spatial = spatial[
            :segment_length
        ]

        final_left[
            start_sample:end_sample
        ] += spatial[:, 0]

        final_right[
            start_sample:end_sample
        ] += spatial[:, 1]

        event_mask[
            start_sample:end_sample
        ] = True

    # Preserve uncovered audio
    uncovered = ~event_mask

    final_left[uncovered] += (
        mono[uncovered] * 0.5
    )

    final_right[uncovered] += (
        mono[uncovered] * 0.5
    )

    final_stereo = np.column_stack(
        (
            final_left,
            final_right
        )
    )

    # Peak protection
    peak = np.max(
        np.abs(final_stereo)
    )

    if peak > 0.98:

        final_stereo = (
            final_stereo / peak
        ) * 0.98

    sf.write(
        str(final_output),
        final_stereo,
        sample_rate
    )

    # ======================================================
    # COMPLETE
    # ======================================================

    print("\n================================================")
    print("              SYSTEM COMPLETE")
    print("================================================")

    print("\n✓ AI Sound Detection")
    print("✓ Decision Engine")
    print("✓ Priority Engine")
    print("✓ Event Merging")
    print("✓ Event Timeline")
    print("✓ Adaptive DSP")
    print("✓ Smart Localization")
    print("✓ GCC-PHAT")
    print("✓ Spatial Rendering")

    print("\nAdaptive Audio:")
    print(adaptive_output)

    print("\nFinal 3D Audio:")
    print(final_output)

    print("\n================================================")


if __name__ == "__main__":

    base_dir = Path(__file__).resolve().parent

    input_audio = (
        base_dir
        / "test_audio"
        / "mic_test.wav"
    )

    run_pipeline(
        input_audio
    )
from pathlib import Path

import numpy as np
import soundfile as sf

from ai.classifier import detect_sounds

from priority.decision_engine import DecisionEngine
from priority.priority_engine import PriorityEngine
from priority.event_merger import merge_events

from localization.smart_localizer import SmartLocalizer

from audio.adaptive_processor import (
    AdaptiveSpectralProcessor
)

from spatial.hrtf import HRTFRenderer


# ==========================================================
# CONFIDENCE
# ==========================================================

def get_confidence(event):

    if "score" in event:
        return float(event["score"])

    if "confidence" in event:
        return float(event["confidence"])

    return 0.0


# ==========================================================
# MAIN PIPELINE
# ==========================================================

def analyze_audio_for_gui(audio_file):

    audio_file = Path(
        audio_file
    ).resolve()

    project_root = (
        Path(__file__).resolve().parent
    )

    output_dir = (
        project_root
        / "output"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    adaptive_output = (
        output_dir
        / "adaptive_spectral.wav"
    )

    spatial_output = (
        output_dir
        / "final_3d_audio.wav"
    )

    # ======================================================
    # STEP 1 — AI
    # ======================================================

    print("\n==============================================")
    print("          AI SOUND ANALYSIS")
    print("==============================================\n")

    detections = detect_sounds(
        audio_file
    )

    if not detections:
        return None

    # ======================================================
    # STEP 2 — DECISION
    # ======================================================

    decision_engine = DecisionEngine(
        confidence_threshold=0.20
    )

    selected_events = (
        decision_engine.create_decisions(
            detections
        )
    )

    if not selected_events:
        return None

    # ======================================================
    # STEP 3 — PRIORITY
    # ======================================================

    priority_engine = PriorityEngine()

    priority_events = []

    for event in selected_events:

        label = event.get(
            "label",
            "Unknown"
        )

        confidence = get_confidence(
            event
        )

        priority_result = (
            priority_engine.get_priority(
                label,
                confidence
            )
        )

        priority_events.append(
            {
                "start": float(
                    event.get(
                        "start",
                        0.0
                    )
                ),

                "end": float(
                    event.get(
                        "end",
                        0.0
                    )
                ),

                "label": label,

                "score": confidence,

                "priority":
                    priority_result["priority"],

                "action":
                    priority_result["action"]
            }
        )

    # ======================================================
    # STEP 4 — MERGE
    # ======================================================

    merged_events = merge_events(
        priority_events
    )

    if not merged_events:
        return None

    # ======================================================
    # STEP 5 — LOCALIZATION
    # ======================================================

    localizer = SmartLocalizer(
        audio_file,
        window_ms=250
    )

    final_events = []

    for event in merged_events:

        confidence = get_confidence(
            event
        )

        try:

            location = (
                localizer.localize_event(
                    event["start"],
                    event["end"]
                )
            )

            angle = float(
                location.get(
                    "angle",
                    0.0
                )
            )

            direction = location.get(
                "direction",
                "UNKNOWN"
            )

            tdoa = float(
                location.get(
                    "tdoa",
                    0.0
                )
            )

        except Exception:

            angle = 0.0
            direction = "UNKNOWN"
            tdoa = 0.0

        final_events.append(
            {
                "start":
                    float(
                        event["start"]
                    ),

                "end":
                    float(
                        event["end"]
                    ),

                "label":
                    event["label"],

                "confidence":
                    confidence,

                "priority":
                    event["priority"],

                "action":
                    event["action"],

                "angle":
                    angle,

                "direction":
                    direction,

                "tdoa":
                    tdoa
            }
        )

    # ======================================================
    # STEP 6 — PROFILE-BASED ADAPTIVE DSP
    # ======================================================

    print(
        "\nRunning profile-based adaptive DSP..."
    )

    try:

        processor = (
            AdaptiveSpectralProcessor(
                sample_rate=44100
            )
        )

        processor.process_file(
            audio_file,
            adaptive_output,
            final_events
        )

    except Exception as error:

        print(
            "\nAdaptive DSP failed:"
        )

        print(error)

        return None

    # ======================================================
    # STEP 7 — SPATIAL AUDIO
    # ======================================================

    print(
        "\nRunning spatial audio rendering..."
    )

    processed_audio, sample_rate = sf.read(
        str(adaptive_output),
        always_2d=True
    )

    mono = np.mean(
        processed_audio,
        axis=1
    ).astype(
        np.float32
    )

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

    for event in final_events:

        start_sample = int(
            event["start"]
            * sample_rate
        )

        end_sample = int(
            event["end"]
            * sample_rate
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

        spatial_segment = renderer.render(
            segment,
            event["angle"]
        )

        segment_length = (
            end_sample
            - start_sample
        )

        spatial_segment = (
            spatial_segment[
                :segment_length
            ]
        )

        final_left[
            start_sample:end_sample
        ] += spatial_segment[:, 0]

        final_right[
            start_sample:end_sample
        ] += spatial_segment[:, 1]

        event_mask[
            start_sample:end_sample
        ] = True

    # ------------------------------------------------------
    # Preserve uncovered audio
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # Peak protection
    # ------------------------------------------------------

    peak = np.max(
        np.abs(final_stereo)
    )

    if peak > 0.98:

        final_stereo = (
            final_stereo / peak
        ) * 0.98

    sf.write(
        str(spatial_output),
        final_stereo,
        sample_rate
    )

    # ======================================================
    # RETURN
    # ======================================================

    return {
        "events":
            final_events,

        "adaptive_audio":
            adaptive_output,

        "spatial_audio":
            spatial_output
    }
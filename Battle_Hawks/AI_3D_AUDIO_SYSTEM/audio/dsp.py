import numpy as np
import soundfile as sf
from pathlib import Path


# ==========================================================
# AUDIO DSP
# ==========================================================

def apply_gain(audio, gain_db):
    """
    Increase or decrease audio volume.

    gain_db:
        +6 dB  -> louder
        0 dB   -> unchanged
        -6 dB  -> quieter
    """

    gain = 10 ** (gain_db / 20)

    processed = audio * gain

    return processed


def prevent_clipping(audio):
    """
    Prevent audio from exceeding -1.0 to +1.0.
    """

    peak = np.max(np.abs(audio))

    if peak > 0.98:
        audio = audio / peak * 0.98

    return audio


# ==========================================================
# PROCESS AUDIO WINDOW
# ==========================================================

def process_window(audio, action):

    if action == "ENHANCE":

        # Moderate enhancement for important sounds
        processed = apply_gain(
            audio,
            +3
        )

    elif action == "SUPPRESS":

        # Reduce background/distracting audio
        processed = apply_gain(
            audio,
            -6
        )

    elif action == "PRESERVE_LIMIT":

        # Critical sound:
        # Do NOT amplify aggressively.
        # Preserve it while preventing clipping.
        processed = audio.copy()

        # Soft peak protection
        peak = np.max(np.abs(processed))

        if peak > 0.80:

            processed = (
                processed / peak
            ) * 0.80

    elif action == "PRESERVE":

        processed = audio.copy()

    else:

        processed = audio.copy()

    return processed


# ==========================================================
# PROCESS COMPLETE AUDIO
# ==========================================================

def process_audio_file(
    input_file,
    output_file,
    actions
):

    input_file = Path(input_file)
    output_file = Path(output_file)

    # ------------------------------------------------------
    # Read audio
    # ------------------------------------------------------

    audio, sample_rate = sf.read(str(input_file))

    print("\n==============================================")
    print("             AUDIO DSP PROCESSING")
    print("==============================================\n")

    print(f"Input file  : {input_file.name}")
    print(f"Sample rate : {sample_rate} Hz")

    # ------------------------------------------------------
    # Convert stereo handling
    # ------------------------------------------------------

    if audio.ndim == 1:

        processed_audio = audio.copy()

    else:

        processed_audio = audio.copy()

    # ------------------------------------------------------
    # Apply processing windows
    # ------------------------------------------------------

    for item in actions:

        start = item["start"]
        end = item["end"]
        action = item["action"]

        start_sample = int(start * sample_rate)
        end_sample = int(end * sample_rate)

        start_sample = max(0, start_sample)
        end_sample = min(
            len(processed_audio),
            end_sample
        )

        if start_sample >= end_sample:
            continue

        processed_audio[
            start_sample:end_sample
        ] = process_window(
            processed_audio[
                start_sample:end_sample
            ],
            action
        )

        print(
            f"{start:05.2f}s - "
            f"{end:05.2f}s → "
            f"{action}"
        )

    # ------------------------------------------------------
    # Prevent clipping
    # ------------------------------------------------------

    processed_audio = prevent_clipping(
        processed_audio
    )

    # ------------------------------------------------------
    # Save
    # ------------------------------------------------------

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    sf.write(
        str(output_file),
        processed_audio,
        sample_rate
    )

    print("\n----------------------------------------------")
    print("Processed audio saved successfully!")
    print(f"Output: {output_file}")
    print("----------------------------------------------\n")


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    BASE_DIR = Path(__file__).resolve().parent.parent

    input_file = (
        BASE_DIR
        / "test_audio"
        / "mic_test.wav"
    )

    output_file = (
        BASE_DIR
        / "output"
        / "dsp_test.wav"
    )

    test_actions = [

        {
            "start": 0.0,
            "end": 0.8,
            "action": "STRONG_ENHANCE"
        },

        {
            "start": 0.8,
            "end": 1.5,
            "action": "ENHANCE"
        },

        {
            "start": 1.5,
            "end": 2.3,
            "action": "SUPPRESS"
        }
    ]

    process_audio_file(
        input_file,
        output_file,
        test_actions
    )
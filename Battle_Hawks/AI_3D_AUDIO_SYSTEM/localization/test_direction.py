from pathlib import Path

import numpy as np
import soundfile as sf


# ==========================================================
# CREATE TEST SIGNAL
# ==========================================================

def create_test_signal(
    sample_rate=44100,
    duration=2.0,
    frequency=700
):
    """
    Create a short test tone.
    """

    total_samples = int(
        sample_rate * duration
    )

    t = np.arange(
        total_samples
    ) / sample_rate

    signal = (
        0.5
        * np.sin(
            2 * np.pi * frequency * t
        )
    )

    # Fade in/out
    fade_samples = int(
        0.02 * sample_rate
    )

    fade = np.linspace(
        0,
        1,
        fade_samples
    )

    signal[:fade_samples] *= fade

    signal[-fade_samples:] *= fade[::-1]

    return signal.astype(
        np.float32
    )


# ==========================================================
# DELAY SIGNAL
# ==========================================================

def delay_signal(signal, delay_samples):

    if delay_samples <= 0:

        return signal.copy()

    delayed = np.zeros_like(
        signal
    )

    delayed[delay_samples:] = (
        signal[:-delay_samples]
    )

    return delayed


# ==========================================================
# CREATE TDOA TEST
# ==========================================================

def create_stereo_test(
    mono,
    position,
    sample_rate=44100
):
    """
    Create stereo signals with an actual
    time difference between channels.

    This is specifically for testing GCC-PHAT.
    """

    left = np.zeros_like(mono)
    right = np.zeros_like(mono)

    # 8 cm microphone spacing
    microphone_distance = 0.08

    # Speed of sound
    speed_of_sound = 343.0

    # Maximum physical TDOA
    max_tdoa = (
        microphone_distance
        / speed_of_sound
    )

    # Use 70% of max TDOA so the test
    # stays inside a realistic range.
    test_tdoa = 0.70 * max_tdoa

    delay_samples = int(
        abs(test_tdoa)
        * sample_rate
    )

    # ------------------------------------------------------
    # LEFT
    # ------------------------------------------------------

    if position == "LEFT":

        left = mono.copy()

        right = delay_signal(
            mono,
            delay_samples
        )

    # ------------------------------------------------------
    # CENTER
    # ------------------------------------------------------

    elif position == "CENTER":

        left = mono.copy()
        right = mono.copy()

    # ------------------------------------------------------
    # RIGHT
    # ------------------------------------------------------

    elif position == "RIGHT":

        right = mono.copy()

        left = delay_signal(
            mono,
            delay_samples
        )

    else:

        raise ValueError(
            "Position must be LEFT, CENTER or RIGHT."
        )

    stereo = np.column_stack(
        (
            left,
            right
        )
    )

    return stereo


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    base_dir = (
        Path(__file__)
        .resolve()
        .parent
        .parent
    )

    output_dir = (
        base_dir
        / "test_audio"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    sample_rate = 44100

    mono = create_test_signal(
        sample_rate=sample_rate,
        duration=2.0
    )

    positions = [
        "LEFT",
        "CENTER",
        "RIGHT"
    ]

    print("\n==============================================")
    print("       TDOA TEST SIGNAL GENERATOR")
    print("==============================================\n")

    for position in positions:

        stereo = create_stereo_test(
            mono,
            position,
            sample_rate
        )

        output_file = (
            output_dir
            / f"{position.lower()}_test.wav"
        )

        sf.write(
            str(output_file),
            stereo,
            sample_rate
        )

        print(
            f"{position:<10} → "
            f"{output_file.name}"
        )

    print("\nTDOA test files created successfully.")
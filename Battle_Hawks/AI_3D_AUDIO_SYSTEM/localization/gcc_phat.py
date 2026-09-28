from pathlib import Path

import numpy as np
import soundfile as sf


# ==========================================================
# GCC-PHAT
# ==========================================================

def gcc_phat(
    signal_left,
    signal_right,
    sample_rate,
    microphone_distance=0.08,
    speed_of_sound=343.0
):
    """
    GCC-PHAT with physically valid TDOA limits.

    microphone_distance:
        Distance between microphones in meters.

    Example:
        0.08 = 8 cm
    """

    signal_left = np.asarray(
        signal_left,
        dtype=np.float64
    )

    signal_right = np.asarray(
        signal_right,
        dtype=np.float64
    )

    # ------------------------------------------------------
    # Same length
    # ------------------------------------------------------

    length = min(
        len(signal_left),
        len(signal_right)
    )

    if length < 32:
        return 0.0

    signal_left = signal_left[:length]
    signal_right = signal_right[:length]

    # ------------------------------------------------------
    # Remove DC
    # ------------------------------------------------------

    signal_left -= np.mean(
        signal_left
    )

    signal_right -= np.mean(
        signal_right
    )

    # ------------------------------------------------------
    # Window
    # ------------------------------------------------------

    window = np.hanning(
        length
    )

    signal_left *= window
    signal_right *= window

    # ------------------------------------------------------
    # FFT
    # ------------------------------------------------------

    fft_size = 1

    while fft_size < 2 * length:
        fft_size *= 2

    left_fft = np.fft.rfft(
        signal_left,
        n=fft_size
    )

    right_fft = np.fft.rfft(
        signal_right,
        n=fft_size
    )

    # ------------------------------------------------------
    # Cross power spectrum
    # ------------------------------------------------------

    cross_power = (
        left_fft
        * np.conj(right_fft)
    )

    magnitude = np.abs(
        cross_power
    )

    magnitude[
        magnitude < 1e-12
    ] = 1e-12

    cross_power /= magnitude

    # ------------------------------------------------------
    # GCC-PHAT correlation
    # ------------------------------------------------------

    correlation = np.fft.irfft(
        cross_power,
        n=fft_size
    )

    # ------------------------------------------------------
    # Maximum physically possible TDOA
    # ------------------------------------------------------

    max_tdoa = (
        microphone_distance
        / speed_of_sound
    )

    max_shift = int(
        np.ceil(
            max_tdoa
            * sample_rate
        )
    )

    max_shift = min(
        max_shift,
        length - 1
    )

    # ------------------------------------------------------
    # Signed lag representation
    # ------------------------------------------------------

    correlation = np.concatenate(
        (
            correlation[-max_shift:],
            correlation[:max_shift + 1]
        )
    )

    lags = np.arange(
        -max_shift,
        max_shift + 1
    )

    # ------------------------------------------------------
    # Find peak
    # ------------------------------------------------------

    peak_index = np.argmax(
        np.abs(correlation)
    )

    shift = lags[
        peak_index
    ]

    tdoa = (
        shift
        / sample_rate
    )

    # ------------------------------------------------------
    # Physical clamp
    # ------------------------------------------------------

    tdoa = np.clip(
        tdoa,
        -max_tdoa,
        max_tdoa
    )

    return float(
        tdoa
    )


# ==========================================================
# TDOA → ANGLE
# ==========================================================

def tdoa_to_angle(
    tdoa,
    microphone_distance=0.08,
    speed_of_sound=343.0
):
    """
    Convert TDOA into prototype azimuth estimate.

    Negative angle:
        Left side

    Positive angle:
        Right side
    """

    if microphone_distance <= 0:

        raise ValueError(
            "Microphone distance must be greater than 0."
        )

    max_tdoa = (
        microphone_distance
        / speed_of_sound
    )

    # ------------------------------------------------------
    # Physical clamp
    # ------------------------------------------------------

    tdoa = np.clip(
        tdoa,
        -max_tdoa,
        max_tdoa
    )

    value = (
        tdoa
        * speed_of_sound
    ) / microphone_distance

    value = np.clip(
        value,
        -1.0,
        1.0
    )

    angle = np.degrees(
        np.arcsin(
            value
        )
    )

    return float(
        angle
    )


# ==========================================================
# ANGLE → DIRECTION
# ==========================================================

def angle_to_direction(angle):
    """
    Convert azimuth angle into a more descriptive
    directional zone.

    Angle convention:

        -90° ................. +90°
          LEFT                 RIGHT

    Zones:

        <= -20°  → LEFT
        -20°...-5° → FRONT-LEFT
        -5°...+5°  → CENTER / FRONT
        +5°...+20° → FRONT-RIGHT
        >= +20°    → RIGHT

    IMPORTANT:
    This is an azimuth estimate from a two-channel
    prototype. It does not prove front/rear 3D position.
    """

    angle = float(
        angle
    )

    # ------------------------------------------------------
    # Strong LEFT
    # ------------------------------------------------------

    if angle <= -20.0:

        return "LEFT"

    # ------------------------------------------------------
    # Slight LEFT
    # ------------------------------------------------------

    elif angle < -5.0:

        return "FRONT-LEFT"

    # ------------------------------------------------------
    # CENTER
    # ------------------------------------------------------

    elif angle <= 5.0:

        return "CENTER / FRONT"

    # ------------------------------------------------------
    # Slight RIGHT
    # ------------------------------------------------------

    elif angle < 20.0:

        return "FRONT-RIGHT"

    # ------------------------------------------------------
    # Strong RIGHT
    # ------------------------------------------------------

    else:

        return "RIGHT"


# ==========================================================
# COMPLETE LOCALIZATION
# ==========================================================

def localize_segment(
    left,
    right,
    sample_rate,
    microphone_distance=0.08
):

    tdoa = gcc_phat(
        left,
        right,
        sample_rate,
        microphone_distance
    )

    angle = tdoa_to_angle(
        tdoa,
        microphone_distance
    )

    direction = angle_to_direction(
        angle
    )

    return {
        "tdoa": tdoa,
        "angle": angle,
        "direction": direction
    }


# ==========================================================
# LOCALIZE FILE SEGMENT
# ==========================================================

def localize_file_segment(
    file_path,
    start_time,
    end_time,
    microphone_distance=0.08
):

    file_path = Path(
        file_path
    ).resolve()

    audio, sample_rate = sf.read(
        str(file_path),
        always_2d=True
    )

    # ------------------------------------------------------
    # Require stereo
    # ------------------------------------------------------

    if audio.shape[1] < 2:

        raise ValueError(
            "Stereo audio with two channels is required."
        )

    start_sample = int(
        start_time
        * sample_rate
    )

    end_sample = int(
        end_time
        * sample_rate
    )

    start_sample = max(
        0,
        start_sample
    )

    end_sample = min(
        len(audio),
        end_sample
    )

    if start_sample >= end_sample:

        raise ValueError(
            "Invalid time range."
        )

    # ------------------------------------------------------
    # Extract L/R channels
    # ------------------------------------------------------

    left = audio[
        start_sample:end_sample,
        0
    ]

    right = audio[
        start_sample:end_sample,
        1
    ]

    # ------------------------------------------------------
    # Localize
    # ------------------------------------------------------

    result = localize_segment(
        left,
        right,
        sample_rate,
        microphone_distance
    )

    # ------------------------------------------------------
    # Print
    # ------------------------------------------------------

    print(
        "\n=============================================="
    )

    print(
        "        EVENT-SPECIFIC GCC-PHAT"
    )

    print(
        "=============================================="
    )

    print(
        f"\nTime window : "
        f"{start_time:.2f}s - "
        f"{end_time:.2f}s"
    )

    print(
        f"TDOA        : "
        f"{result['tdoa'] * 1000:.3f} ms"
    )

    print(
        f"Angle       : "
        f"{result['angle']:.2f}°"
    )

    print(
        f"Direction   : "
        f"{result['direction']}"
    )

    print(
        "\nMaximum physically possible TDOA "
        "for 8 cm spacing: "
        f"{(microphone_distance / 343.0) * 1000:.3f} ms"
    )

    return result


# ==========================================================
# TEST
# ==========================================================

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

    localize_file_segment(
        audio_file,
        start_time=0.0,
        end_time=1.0
    )
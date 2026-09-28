from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import stft, istft


def db_to_gain(db):
    return 10 ** (db / 20.0)


def selective_process(
    input_file,
    output_file,
    gain_db=3.0,
    suppress_db=-6.0
):
    """
    Basic STFT-based selective audio processing framework.

    This version demonstrates the processing pipeline.
    It does NOT yet perform true source separation.
    """

    input_file = Path(input_file).resolve()
    output_file = Path(output_file).resolve()

    print("\n==============================================")
    print("       SELECTIVE AUDIO PROCESSOR")
    print("==============================================\n")

    print(f"Input file : {input_file}")

    # ------------------------------------------------------
    # Load audio
    # ------------------------------------------------------

    audio, sample_rate = sf.read(
        str(input_file),
        always_2d=False
    )

    print(f"Sample rate: {sample_rate} Hz")

    # ------------------------------------------------------
    # Handle mono/stereo
    # ------------------------------------------------------

    if audio.ndim == 1:

        channels = [audio]

    else:

        channels = [
            audio[:, channel]
            for channel in range(audio.shape[1])
        ]

    processed_channels = []

    # ------------------------------------------------------
    # Process each channel
    # ------------------------------------------------------

    for channel_index, channel_audio in enumerate(channels):

        # STFT
        frequencies, times, Zxx = stft(
            channel_audio,
            fs=sample_rate,
            nperseg=1024,
            noverlap=768
        )

        magnitude = np.abs(Zxx)

        # --------------------------------------------------
        # Temporary frequency mask
        # --------------------------------------------------
        #
        # This is only a demonstration.
        # Later the AI/separation model will generate
        # meaningful sound-specific masks.
        #

        mask = np.ones_like(magnitude)

        # Lower-frequency background suppression
        low_frequency_limit = 120

        mask[
            frequencies < low_frequency_limit,
            :
        ] *= db_to_gain(suppress_db)

        # Moderate high-frequency enhancement
        high_frequency_start = 2500

        mask[
            frequencies > high_frequency_start,
            :
        ] *= db_to_gain(gain_db)

        # Apply mask to complex STFT
        Z_processed = Zxx * mask

        # Inverse STFT
        _, reconstructed = istft(
            Z_processed,
            fs=sample_rate,
            nperseg=1024,
            noverlap=768
        )

        processed_channels.append(
            reconstructed
        )

    # ------------------------------------------------------
    # Match lengths
    # ------------------------------------------------------

    min_length = min(
        len(channel)
        for channel in processed_channels
    )

    processed_channels = [
        channel[:min_length]
        for channel in processed_channels
    ]

    # ------------------------------------------------------
    # Recombine channels
    # ------------------------------------------------------

    if len(processed_channels) == 1:

        output_audio = processed_channels[0]

    else:

        output_audio = np.column_stack(
            processed_channels
        )

    # ------------------------------------------------------
    # Prevent clipping
    # ------------------------------------------------------

    peak = np.max(
        np.abs(output_audio)
    )

    if peak > 0.98:

        output_audio = (
            output_audio / peak
        ) * 0.98

    # ------------------------------------------------------
    # Save
    # ------------------------------------------------------

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    sf.write(
        str(output_file),
        output_audio,
        sample_rate
    )

    print("\nProcessing complete.")
    print(f"Output file: {output_file}")


if __name__ == "__main__":

    base_dir = Path(__file__).resolve().parent.parent

    input_file = (
        base_dir
        / "test_audio"
        / "mic_test.wav"
    )

    output_file = (
        base_dir
        / "output"
        / "selective_test.wav"
    )

    selective_process(
        input_file,
        output_file
    )
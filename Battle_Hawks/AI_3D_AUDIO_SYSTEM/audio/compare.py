from pathlib import Path

import numpy as np
import soundfile as sf


def rms(audio):
    return float(
        np.sqrt(
            np.mean(
                np.square(audio.astype(np.float64))
            )
        )
    )


def peak(audio):
    return float(
        np.max(
            np.abs(audio)
        )
    )


def analyze(file_path):

    audio, sr = sf.read(
        str(file_path)
    )

    return {
        "sample_rate": sr,
        "duration": len(audio) / sr,
        "channels": 1 if audio.ndim == 1 else audio.shape[1],
        "rms": rms(audio),
        "peak": peak(audio)
    }


if __name__ == "__main__":

    base_dir = Path(__file__).resolve().parent.parent

    original = (
        base_dir
        / "test_audio"
        / "mic_test.wav"
    )

    processed = (
        base_dir
        / "output"
        / "ai_processed.wav"
    )

    original_info = analyze(original)
    processed_info = analyze(processed)

    print("\n==============================================")
    print("          ORIGINAL vs PROCESSED")
    print("==============================================\n")

    print("ORIGINAL AUDIO")
    print("----------------------------------------------")
    print(
        f"Sample Rate : "
        f"{original_info['sample_rate']} Hz"
    )
    print(
        f"Duration    : "
        f"{original_info['duration']:.2f} sec"
    )
    print(
        f"Channels    : "
        f"{original_info['channels']}"
    )
    print(
        f"RMS         : "
        f"{original_info['rms']:.6f}"
    )
    print(
        f"Peak        : "
        f"{original_info['peak']:.6f}"
    )

    print("\nPROCESSED AUDIO")
    print("----------------------------------------------")
    print(
        f"Sample Rate : "
        f"{processed_info['sample_rate']} Hz"
    )
    print(
        f"Duration    : "
        f"{processed_info['duration']:.2f} sec"
    )
    print(
        f"Channels    : "
        f"{processed_info['channels']}"
    )
    print(
        f"RMS         : "
        f"{processed_info['rms']:.6f}"
    )
    print(
        f"Peak        : "
        f"{processed_info['peak']:.6f}"
    )

    print("\n==============================================")
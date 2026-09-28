from pathlib import Path

import numpy as np
import soundfile as sf
import librosa
import librosa.display
import matplotlib.pyplot as plt


def analyze_audio(file_path):

    print("\n================ AUDIO ANALYSIS ================\n")

    # Get absolute file path
    file_path = Path(file_path).resolve()

    print(f"Checking file:\n{file_path}\n")

    # Check whether file exists
    if not file_path.exists():
        print("ERROR: Audio file does not exist!")
        return

    print("File found successfully!")

    try:
        # Read audio
        audio, sample_rate = sf.read(str(file_path))

    except Exception as e:
        print("\nERROR while reading audio file:")
        print(e)
        return

    # Number of channels
    if audio.ndim == 1:
        channels = 1
        mono_audio = audio
    else:
        channels = audio.shape[1]
        mono_audio = np.mean(audio, axis=1)

    # Duration
    duration = len(mono_audio) / sample_rate

    # RMS
    rms = librosa.feature.rms(y=mono_audio)[0]

    print("\n------------- AUDIO INFORMATION -------------")
    print(f"File           : {file_path.name}")
    print(f"Sample Rate    : {sample_rate} Hz")
    print(f"Channels       : {channels}")
    print(f"Duration       : {duration:.2f} seconds")
    print(f"Average Energy : {np.mean(rms):.4f}")
    print(f"Maximum Energy : {np.max(rms):.4f}")
    print("----------------------------------------------\n")

    # ==================================================
    # WAVEFORM
    # ==================================================

    plt.figure(figsize=(12, 4))

    librosa.display.waveshow(
        mono_audio,
        sr=sample_rate
    )

    plt.title("Audio Waveform")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")

    plt.tight_layout()
    plt.show()

    # ==================================================
    # SPECTROGRAM
    # ==================================================

    spectrogram = librosa.feature.melspectrogram(
        y=mono_audio,
        sr=sample_rate,
        n_mels=128
    )

    spectrogram_db = librosa.power_to_db(
        spectrogram,
        ref=np.max
    )

    plt.figure(figsize=(12, 5))

    librosa.display.specshow(
        spectrogram_db,
        sr=sample_rate,
        x_axis="time",
        y_axis="mel"
    )

    plt.colorbar(format="%+2.0f dB")

    plt.title("Audio Spectrogram")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Frequency")

    plt.tight_layout()
    plt.show()


# ======================================================
# MAIN
# ======================================================

if __name__ == "__main__":

    BASE_DIR = Path(__file__).resolve().parent.parent

    audio_file = BASE_DIR / "test_audio" / "mic_test.wav"

    analyze_audio(audio_file)
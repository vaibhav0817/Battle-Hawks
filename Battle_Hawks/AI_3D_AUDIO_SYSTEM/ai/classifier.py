from pathlib import Path

import numpy as np
import soundfile as sf
import librosa
import torch 
from transformers import pipeline


# ==========================================================
# AI MODEL
# ==========================================================

MODEL_NAME = "MIT/ast-finetuned-audioset-10-10-0.4593"


print("\nLoading AI Sound Detection Model...")
print("First time may take some time because the model is downloaded.\n")


classifier = pipeline(
    task="audio-classification",
    model=MODEL_NAME,
    device=0 if torch.cuda.is_available() else -1
)


print("AI Model loaded successfully!")


# ==========================================================
# AUDIO DETECTION
# ==========================================================

def detect_sounds(file_path):

    file_path = Path(file_path).resolve()

    print("\n==============================================")
    print("       AI SOUND EVENT DETECTION")
    print("==============================================\n")

    print("Audio file:")
    print(file_path)

    # ------------------------------------------------------
    # Load audio
    # ------------------------------------------------------

    audio, sample_rate = sf.read(str(file_path))

    # Convert stereo → mono for AI detection
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    print(f"\nOriginal Sample Rate : {sample_rate} Hz")
    print(f"Duration             : {len(audio) / sample_rate:.2f} sec")

    # ------------------------------------------------------
    # AI model works with 16 kHz audio
    # ------------------------------------------------------

    target_sr = 16000

    if sample_rate != target_sr:

        audio = librosa.resample(
            audio.astype(np.float32),
            orig_sr=sample_rate,
            target_sr=target_sr
        )

        sample_rate = target_sr

    print(f"AI Sample Rate        : {sample_rate} Hz")

    # ------------------------------------------------------
    # Divide audio into windows
    # ------------------------------------------------------

    window_seconds = 1.0
    hop_seconds = 0.5

    window_size = int(window_seconds * sample_rate)
    hop_size = int(hop_seconds * sample_rate)

    results = []

    # ------------------------------------------------------
    # Analyze each audio window
    # ------------------------------------------------------

    for start in range(0, len(audio) - window_size + 1, hop_size):

        end = start + window_size

        chunk = audio[start:end]

        start_time = start / sample_rate
        end_time = end / sample_rate

        try:

            predictions = classifier(
                {
                    "array": chunk.astype(np.float32),
                    "sampling_rate": sample_rate
                },
                top_k=5
            )

        except Exception as e:

            print("\nAI ERROR:")
            print(e)
            continue

        # --------------------------------------------------
        # Print results
        # --------------------------------------------------

        print(
            f"\n[{start_time:05.2f}s - {end_time:05.2f}s]"
        )

        for prediction in predictions:

            label = prediction["label"]
            score = prediction["score"]

            print(
                f"   {label:<35} "
                f"{score * 100:6.2f}%"
            )

            results.append(
                {
                    "start": start_time,
                    "end": end_time,
                    "label": label,
                    "score": score
                }
            )

    return results


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    BASE_DIR = Path(__file__).resolve().parent.parent

    audio_file = (
        BASE_DIR
        / "test_audio"
        / "mic_test.wav"
    )

    detect_sounds(audio_file)
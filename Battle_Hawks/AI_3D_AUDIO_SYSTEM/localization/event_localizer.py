from pathlib import Path

import soundfile as sf

from localization.gcc_phat import (
    localize_segment
)


class EventLocalizer:

    def __init__(self, audio_file):

        self.audio_file = Path(
            audio_file
        ).resolve()

        self.audio, self.sample_rate = sf.read(
            str(self.audio_file),
            always_2d=True
        )

    def localize_event(
        self,
        start_time,
        end_time
    ):

        # ------------------------------------------
        # Validate stereo audio
        # ------------------------------------------

        if self.audio.shape[1] < 2:

            raise ValueError(
                "Stereo audio with two channels is required."
            )

        # ------------------------------------------
        # Convert time → samples
        # ------------------------------------------

        start_sample = int(
            start_time * self.sample_rate
        )

        end_sample = int(
            end_time * self.sample_rate
        )

        start_sample = max(
            0,
            start_sample
        )

        end_sample = min(
            len(self.audio),
            end_sample
        )

        if start_sample >= end_sample:

            raise ValueError(
                "Invalid event time range."
            )

        # ------------------------------------------
        # Extract event
        # ------------------------------------------

        left = self.audio[
            start_sample:end_sample,
            0
        ]

        right = self.audio[
            start_sample:end_sample,
            1
        ]

        # ------------------------------------------
        # GCC-PHAT
        # ------------------------------------------

        result = localize_segment(
            left,
            right,
            self.sample_rate
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

    localizer = EventLocalizer(
        audio_file
    )

    result = localizer.localize_event(
        start_time=0.0,
        end_time=1.0
    )

    print("\n==============================================")
    print("             EVENT LOCALIZER")
    print("==============================================\n")

    print(
        f"TDOA      : "
        f"{result['tdoa'] * 1000:.3f} ms"
    )

    print(
        f"Angle     : "
        f"{result['angle']:.2f}°"
    )

    print(
        f"Direction : "
        f"{result['direction']}"
    )
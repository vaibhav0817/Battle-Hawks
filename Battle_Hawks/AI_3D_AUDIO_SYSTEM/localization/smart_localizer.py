from pathlib import Path

import numpy as np
import soundfile as sf

from localization.gcc_phat import localize_segment


class SmartLocalizer:

    def __init__(
        self,
        audio_file,
        window_ms=250
    ):
        self.audio_file = Path(audio_file).resolve()
        self.window_ms = window_ms

        self.audio, self.sample_rate = sf.read(
            str(self.audio_file),
            always_2d=True
        )

        if self.audio.shape[1] < 2:
            raise ValueError(
                "Two-channel stereo audio is required."
            )

    def get_event_segment(
        self,
        start_time,
        end_time
    ):
        """
        Extract the highest-energy short window
        inside the detected event.
        """

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
                "Invalid event range."
            )

        event = self.audio[
            start_sample:end_sample
        ]

        window_samples = int(
            self.window_ms
            * self.sample_rate
            / 1000
        )

        # If event is shorter than requested window
        if len(event) <= window_samples:
            return (
                start_sample,
                end_sample,
                event
            )

        # ------------------------------------------
        # Find highest-energy location
        # ------------------------------------------

        mono = np.mean(
            event,
            axis=1
        )

        best_start = 0
        best_energy = -np.inf

        step = max(
            1,
            window_samples // 4
        )

        for i in range(
            0,
            len(event) - window_samples + 1,
            step
        ):

            segment = mono[
                i:i + window_samples
            ]

            energy = np.mean(
                segment ** 2
            )

            if energy > best_energy:

                best_energy = energy
                best_start = i

        best_end = (
            best_start
            + window_samples
        )

        return (
            start_sample + best_start,
            start_sample + best_end,
            event[
                best_start:best_end
            ]
        )

    def localize_event(
        self,
        start_time,
        end_time
    ):

        (
            segment_start,
            segment_end,
            segment
        ) = self.get_event_segment(
            start_time,
            end_time
        )

        left = segment[:, 0]
        right = segment[:, 1]

        result = localize_segment(
            left,
            right,
            self.sample_rate
        )

        result["analysis_start"] = (
            segment_start / self.sample_rate
        )

        result["analysis_end"] = (
            segment_end / self.sample_rate
        )

        return result


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

    localizer = SmartLocalizer(
        audio_file,
        window_ms=250
    )

    result = localizer.localize_event(
        0.0,
        1.0
    )

    print("\n==============================================")
    print("           SMART EVENT LOCALIZER")
    print("==============================================\n")

    print(
        f"Analysis window : "
        f"{result['analysis_start']:.3f}s - "
        f"{result['analysis_end']:.3f}s"
    )

    print(
        f"TDOA            : "
        f"{result['tdoa'] * 1000:.3f} ms"
    )

    print(
        f"Angle           : "
        f"{result['angle']:.2f}°"
    )

    print(
        f"Direction       : "
        f"{result['direction']}"
    )
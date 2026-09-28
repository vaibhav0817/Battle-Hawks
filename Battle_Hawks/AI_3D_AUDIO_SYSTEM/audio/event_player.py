from pathlib import Path
import winsound

import soundfile as sf


class EventPlayer:

    def __init__(self):
        self.temp_file = None

    def play_event(
        self,
        audio_file,
        start_time,
        end_time
    ):

        audio_file = Path(
            audio_file
        ).resolve()

        if not audio_file.exists():
            raise FileNotFoundError(
                f"Audio file not found:\n{audio_file}"
            )

        audio, sample_rate = sf.read(
            str(audio_file),
            always_2d=True
        )

        start_sample = int(
            start_time * sample_rate
        )

        end_sample = int(
            end_time * sample_rate
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
                "Invalid event time range."
            )

        event_audio = audio[
            start_sample:end_sample
        ]

        # Temporary event file
        temp_dir = (
            Path(__file__)
            .resolve()
            .parent.parent
            / "output"
        )

        temp_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.temp_file = (
            temp_dir
            / "selected_event.wav"
        )

        sf.write(
            str(self.temp_file),
            event_audio,
            sample_rate
        )

        winsound.PlaySound(
            str(self.temp_file),
            winsound.SND_FILENAME
            | winsound.SND_ASYNC
        )

    def stop(self):

        winsound.PlaySound(
            None,
            winsound.SND_PURGE
        )
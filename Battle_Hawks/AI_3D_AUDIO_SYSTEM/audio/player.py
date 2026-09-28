import winsound
from pathlib import Path


class AudioPlayer:

    def __init__(self):
        self.current_file = None

    def play(self, file_path):
        """
        Play a complete WAV file asynchronously.
        """

        file_path = Path(
            file_path
        ).resolve()

        if not file_path.exists():
            raise FileNotFoundError(
                f"Audio file not found:\n{file_path}"
            )

        if file_path.suffix.lower() != ".wav":
            raise ValueError(
                "Only WAV files are supported."
            )

        self.current_file = file_path

        winsound.PlaySound(
            str(file_path),
            winsound.SND_FILENAME
            | winsound.SND_ASYNC
        )

    def stop(self):
        """
        Stop playback.
        """

        winsound.PlaySound(
            None,
            winsound.SND_PURGE
        )

        self.current_file = None
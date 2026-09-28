from pathlib import Path

import soundfile as sf

from localization.gcc_phat import (
    localize_segment
)


def test_file(file_path):

    audio, sample_rate = sf.read(
        str(file_path),
        always_2d=True
    )

    if audio.shape[1] < 2:

        print(
            f"{file_path.name}: "
            "ERROR - stereo file required"
        )

        return

    left = audio[:, 0]
    right = audio[:, 1]

    result = localize_segment(
        left,
        right,
        sample_rate
    )

    print(
        f"{file_path.name:<20} "
        f"| Angle = "
        f"{result['angle']:7.2f}° "
        f"| Direction = "
        f"{result['direction']}"
    )


if __name__ == "__main__":

    base_dir = (
        Path(__file__)
        .resolve()
        .parent
        .parent
    )

    test_dir = (
        base_dir
        / "test_audio"
    )

    print("\n==============================================")
    print("             GCC-PHAT VALIDATION")
    print("==============================================\n")

    for filename in [
        "left_test.wav",
        "center_test.wav",
        "right_test.wav"
    ]:

        file_path = (
            test_dir
            / filename
        )

        test_file(
            file_path
        )

    print("\n==============================================")
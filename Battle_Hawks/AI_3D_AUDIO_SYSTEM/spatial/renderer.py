from pathlib import Path

import numpy as np
import soundfile as sf

from spatial.hrtf import HRTFRenderer


def render_file(
    input_file,
    output_file,
    angle
):

    input_file = Path(
        input_file
    ).resolve()

    output_file = Path(
        output_file
    ).resolve()

    audio, sample_rate = sf.read(
        str(input_file),
        always_2d=True
    )

    # Convert input to mono source
    mono = np.mean(
        audio,
        axis=1
    ).astype(np.float32)

    renderer = HRTFRenderer(
        sample_rate
    )

    spatial_audio = renderer.render(
        mono,
        angle
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    sf.write(
        str(output_file),
        spatial_audio,
        sample_rate
    )

    print("\n==============================================")
    print("          HRTF SPATIAL RENDERER")
    print("==============================================\n")

    print(
        f"Input     : {input_file.name}"
    )

    print(
        f"Angle     : {angle:.2f}°"
    )

    print(
        f"Output    : {output_file}"
    )

    print(
        "\nBinaural spatial audio generated."
    )

    print(
        "\nNOTE:"
    )

    print(
        "Current renderer uses a prototype"
    )

    print(
        "placeholder impulse response."
    )

    print(
        "A measured HRTF dataset will be"
    )

    print(
        "integrated in the next stage."
    )


if __name__ == "__main__":

    base_dir = (
        Path(__file__)
        .resolve()
        .parent
        .parent
    )

    input_file = (
        base_dir
        / "test_audio"
        / "mic_test.wav"
    )

    output_file = (
        base_dir
        / "output"
        / "hrtf_test.wav"
    )

    # Current GCC-PHAT result
    angle = 16.96

    render_file(
        input_file,
        output_file,
        angle
    )
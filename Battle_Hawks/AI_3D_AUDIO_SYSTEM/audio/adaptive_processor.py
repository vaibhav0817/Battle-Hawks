from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import stft, istft

from audio.sound_profiles import get_sound_profile


class AdaptiveSpectralProcessor:

    def __init__(
        self,
        sample_rate,
        nperseg=1024,
        noverlap=768
    ):

        self.sample_rate = sample_rate
        self.nperseg = nperseg
        self.noverlap = noverlap

    # ======================================================
    # DB → LINEAR GAIN
    # ======================================================

    @staticmethod
    def db_to_gain(db):

        return 10 ** (
            db / 20.0
        )

    # ======================================================
    # PROCESS CHANNEL WITH PROFILE
    # ======================================================

    def process_channel(
        self,
        audio,
        profile
    ):

        audio = np.asarray(
            audio,
            dtype=np.float32
        )

        # --------------------------------------------------
        # STFT
        # --------------------------------------------------

        frequencies, times, spectrum = stft(
            audio,
            fs=self.sample_rate,
            nperseg=self.nperseg,
            noverlap=self.noverlap
        )

        magnitude = np.abs(
            spectrum
        )

        # --------------------------------------------------
        # Profile parameters
        # --------------------------------------------------

        gain_db = float(
            profile.get(
                "gain_db",
                0.0
            )
        )

        low_cut = float(
            profile.get(
                "low_cut",
                80
            )
        )

        high_cut = float(
            profile.get(
                "high_cut",
                10000
            )
        )

        action = profile.get(
            "action",
            "PRESERVE"
        )

        # --------------------------------------------------
        # Base gain
        # --------------------------------------------------

        gain = np.ones_like(
            magnitude
        )

        base_gain = self.db_to_gain(
            gain_db
        )

        gain *= base_gain

        # --------------------------------------------------
        # Frequency masking
        # --------------------------------------------------

        outside_band = (
            (frequencies < low_cut)
            |
            (frequencies > high_cut)
        )

        # Background/unknown frequencies receive
        # stronger reduction only for suppression profiles.
        if action == "SUPPRESS":

            gain[
                outside_band,
                :
            ] *= self.db_to_gain(
                -8.0
            )

        # --------------------------------------------------
        # Adaptive frame energy
        # --------------------------------------------------

        frame_energy = np.mean(
            magnitude ** 2,
            axis=0
        )

        maximum_energy = (
            np.max(
                frame_energy
            ) + 1e-12
        )

        normalized_energy = (
            frame_energy
            / maximum_energy
        )

        # --------------------------------------------------
        # Frame-by-frame adaptation
        # --------------------------------------------------

        for frame in range(
            magnitude.shape[1]
        ):

            energy = normalized_energy[
                frame
            ]

            # ----------------------------------------------
            # Enhancement
            # ----------------------------------------------

            if action == "ENHANCE":

                if energy > 0.20:

                    gain[
                        :,
                        frame
                    ] *= self.db_to_gain(
                        1.5
                    )

                else:

                    gain[
                        :,
                        frame
                    ] *= self.db_to_gain(
                        -1.0
                    )

            # ----------------------------------------------
            # Background suppression
            # ----------------------------------------------

            elif action == "SUPPRESS":

                if energy < 0.35:

                    gain[
                        :,
                        frame
                    ] *= self.db_to_gain(
                        -4.0
                    )

            # ----------------------------------------------
            # Critical sound
            # ----------------------------------------------

            elif action == "PRESERVE_LIMIT":

                # Keep natural level.
                # No aggressive boost.
                #
                # Peak limiting is applied after
                # reconstruction.
                pass

            # ----------------------------------------------
            # Normal preserve
            # ----------------------------------------------

            elif action == "PRESERVE":

                pass

        # --------------------------------------------------
        # Special speech band
        # --------------------------------------------------

        category = profile.get(
            "category",
            "UNKNOWN"
        )

        if category == "COMMUNICATION":

            speech_band = (
                (frequencies >= 300)
                &
                (frequencies <= 4500)
            )

            gain[
                speech_band,
                :
            ] *= self.db_to_gain(
                1.5
            )

        # --------------------------------------------------
        # Footstep / movement detail
        # --------------------------------------------------

        elif category == "MOVEMENT":

            movement_band = (
                (frequencies >= 150)
                &
                (frequencies <= 6000)
            )

            gain[
                movement_band,
                :
            ] *= self.db_to_gain(
                1.0
            )

        # --------------------------------------------------
        # Apply gain
        # --------------------------------------------------

        processed_spectrum = (
            spectrum * gain
        )

        # --------------------------------------------------
        # ISTFT
        # --------------------------------------------------

        _, processed = istft(
            processed_spectrum,
            fs=self.sample_rate,
            nperseg=self.nperseg,
            noverlap=self.noverlap
        )

        processed = processed[
            :len(audio)
        ]

        return processed.astype(
            np.float32
        )

    # ======================================================
    # PROCESS FILE
    # ======================================================

    def process_file(
        self,
        input_file,
        output_file,
        events=None
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

        self.sample_rate = sample_rate

        # --------------------------------------------------
        # If no events are supplied,
        # use default preserve profile.
        # --------------------------------------------------

        if not events:

            events = [
                {
                    "start": 0.0,
                    "end": len(audio)
                    / sample_rate,
                    "label": "Unknown"
                }
            ]

        # --------------------------------------------------
        # Create output buffer
        # --------------------------------------------------

        processed_audio = np.array(
            audio,
            dtype=np.float32,
            copy=True
        )

        # --------------------------------------------------
        # Process each detected event
        # --------------------------------------------------

        for event in events:

            start_time = float(
                event.get(
                    "start",
                    0.0
                )
            )

            end_time = float(
                event.get(
                    "end",
                    0.0
                )
            )

            label = event.get(
                "label",
                "Unknown"
            )

            # Profile
            profile = get_sound_profile(
                label
            )

            start_sample = int(
                start_time
                * sample_rate
            )

            end_sample = int(
                end_time
                * sample_rate
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
                continue

            # ----------------------------------------------
            # Process each channel
            # ----------------------------------------------

            for channel in range(
                audio.shape[1]
            ):

                segment = audio[
                    start_sample:end_sample,
                    channel
                ]

                processed_segment = (
                    self.process_channel(
                        segment,
                        profile
                    )
                )

                usable_length = min(
                    len(processed_segment),
                    end_sample
                    - start_sample
                )

                processed_audio[
                    start_sample:
                    start_sample + usable_length,
                    channel
                ] = processed_segment[
                    :usable_length
                ]

        # --------------------------------------------------
        # Peak protection
        # --------------------------------------------------

        peak = np.max(
            np.abs(processed_audio)
        )

        if peak > 0.95:

            processed_audio = (
                processed_audio / peak
            ) * 0.95

        # --------------------------------------------------
        # Save
        # --------------------------------------------------

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        sf.write(
            str(output_file),
            processed_audio,
            sample_rate
        )

        return output_file


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

    input_file = (
        base_dir
        / "test_audio"
        / "mic_test.wav"
    )

    output_file = (
        base_dir
        / "output"
        / "profile_based_audio.wav"
    )

    print("\n==============================================")
    print("       PROFILE-BASED AUDIO PROCESSOR")
    print("==============================================\n")

    # Example events
    test_events = [

        {
            "start": 0.0,
            "end": 1.0,
            "label": "Gunshot, gunfire"
        },

        {
            "start": 1.0,
            "end": 2.0,
            "label": "Speech"
        },

        {
            "start": 2.0,
            "end": 3.0,
            "label": "Wind"
        }
    ]

    processor = (
        AdaptiveSpectralProcessor(
            sample_rate=44100
        )
    )

    result = processor.process_file(
        input_file,
        output_file,
        test_events
    )

    print(
        f"Input  : {input_file}"
    )

    print(
        f"Output : {result}"
    )

    print(
        "\nProfile-based processing complete."
    )
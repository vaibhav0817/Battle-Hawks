import numpy as np
from scipy.signal import fftconvolve


class HRTFRenderer:

    def __init__(self, sample_rate):
        self.sample_rate = sample_rate

    def generate_placeholder_hrir(self, angle):
        """
        Prototype placeholder HRIR.

        IMPORTANT:
        This is NOT a measured HRTF.
        It is only used to structure the pipeline.
        """

        ir_length = int(
            0.05 * self.sample_rate
        )

        left_ir = np.zeros(ir_length)
        right_ir = np.zeros(ir_length)

        center = 0

        # Simple direct impulse
        left_ir[center] = 1.0
        right_ir[center] = 1.0

        # Simple level difference
        normalized = np.clip(
            angle / 90.0,
            -1.0,
            1.0
        )

        if normalized > 0:

            left_gain = 0.75
            right_gain = 1.0

        elif normalized < 0:

            left_gain = 1.0
            right_gain = 0.75

        else:

            left_gain = 1.0
            right_gain = 1.0

        left_ir *= left_gain
        right_ir *= right_gain

        return left_ir, right_ir

    def render(self, mono_audio, angle):

        left_ir, right_ir = (
            self.generate_placeholder_hrir(
                angle
            )
        )

        left = fftconvolve(
            mono_audio,
            left_ir
        )

        right = fftconvolve(
            mono_audio,
            right_ir
        )

        min_length = min(
            len(left),
            len(right)
        )

        stereo = np.column_stack(
            (
                left[:min_length],
                right[:min_length]
            )
        )

        # Normalize
        peak = np.max(
            np.abs(stereo)
        )

        if peak > 0.98:

            stereo = (
                stereo / peak
            ) * 0.98

        return stereo
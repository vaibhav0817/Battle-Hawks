# Localization and Spatial Audio

## GCC-PHAT
```text
Multi-channel audio
      ↓
Cross-correlation + PHAT weighting
      ↓
TDOA
      ↓
Direction of Arrival
      ↓
Angle / Direction
```

Record microphone geometry, sample rate, channel ordering and angle convention with each experiment.

## HRTF
Inputs:
- AI-enhanced audio
- Estimated direction/angle

Output:
- 3D binaural audio

The fast limiter path bypasses HRTF and enters the mixer directly.

## Validation
Use controlled source positions and compare estimated angles against ground truth.

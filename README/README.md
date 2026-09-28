# AI 3D Situational Audio System

An AI-powered adaptive tactical audio system designed to detect, prioritize, enhance, and spatially localize battlefield sounds while providing a low-latency safety path.

> **Status:** Academic research prototype / demonstrator. Numerical performance claims should be reported only after measurement.

## Problem
Traditional noise cancellation can suppress useful acoustic information. A tactical system should distinguish critical, useful, and background sounds.

## Core Pipeline
```text
Acoustic Environment
      ↓
4-Mic Array
      ↓
ADC / Codec
      ↓
 ┌────┴───────────────────────┐
 ↓                            ↓
Fast Limiter Path         AI Processing Path
(analog / low latency)    (digital / edge)
 ↓                            ↓
Limited Audio             AI Enhanced Audio
                              ↓
                       Decision + Priority
                              ↓
                         Adaptive DSP
                              ↓
                        GCC-PHAT / DoA
                              ↓
                         HRTF / 3D Audio
                              ↓
 └──────────────→ Mixer ←─────┘
                    ↓
             DAC + Amplifier
                    ↓
             Tactical Headset
```

## Innovation
- **Context-aware audio intelligence:** Detect → Decide → Enhance → Localize → Deliver
- **Hybrid AI + DSP:** AI provides acoustic understanding; DSP provides deterministic processing.
- **Priority-aware audio:** Critical, important, and background events are handled differently.
- **Spatial situational awareness:** GCC-PHAT direction estimation + HRTF spatial rendering.
- **Edge-first design:** Intended for embedded, low-power, real-time deployment.
- **Dual-path safety:** Fast limiter path operates independently of AI decisions.

## Important Routing
The **Fast Limiter Path bypasses HRTF** and goes directly to the mixer. HRTF is applied only to the AI-enhanced path using the estimated direction. The mixer delay-aligns and combines both paths.

## Prototype Dashboard
The software console visualizes:
- Audio waveform/event timeline
- Acoustic direction radar
- Detected event
- Confidence
- Priority
- Action
- Angle and direction
- Processing-module status

The GUI is a validation/demo console for the hardware-oriented processing architecture.

## Hardware
- 4-channel MEMS microphone array
- ADC / codec
- Analog fast-limiter/protection chain
- Raspberry Pi Compute Module-class embedded platform
- Edge AI accelerator
- Delay-aligned mixer
- DAC + amplifier
- Tactical headset

## Software Stack
Python, NumPy, SciPy, Librosa, PyTorch, Hugging Face tooling, ONNX, Hailo tooling, PySide6, CMSIS-DSP, I2S/DMA and Linux, as applicable to the committed implementation.

## Repository Structure
```text
src/          Core processing
hardware/     Schematics, PCB and hardware notes
gui/          Prototype dashboard
models/       Model/checkpoint metadata
tests/        Automated and experiment tests
docs/         Detailed documentation
demo/         Screenshots and demonstration material
data/         Dataset metadata; do not commit restricted datasets
```

## Testing
Measure and document:
- Accuracy / Precision / Recall / F1
- SNR improvement
- STOI
- AI inference latency
- Fast-path latency
- End-to-end latency
- Direction/angle error

Do not label target values as measured results.

## Safety
This repository documents a research prototype, not a certified hearing-protection device. Final deployment requires appropriate acoustic, electrical, EMC/EMI, environmental, system-safety and hearing-protection validation.

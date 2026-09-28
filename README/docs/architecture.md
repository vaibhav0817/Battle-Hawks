# System Architecture

The architecture separates computational AI processing from a low-latency safety path.

## Routing
```text
4-Mic Array → ADC/Codec
                  ├→ Fast Limiter → Limited Digital Audio ─┐
                  └→ AI → Decision → Priority → DSP       │
                                      ↓                    │
                                AI Enhanced Audio          │
                                      ↓                    │
                                GCC-PHAT / DoA             │
                                      ↓                    │
                                HRTF / 3D Audio ───────────┤
                                                           ↓
                                                         Mixer
                                                           ↓
                                                   DAC + Amplifier
                                                           ↓
                                                   Tactical Headset
```

**The fast limiter does not enter HRTF.** It bypasses spatial rendering and reaches the mixer directly.

## Functional Blocks
1. Acoustic capture
2. Analog/digital conversion
3. Fast protection path
4. AI acoustic classification
5. Decision and priority logic
6. Adaptive DSP
7. Localization
8. Spatial rendering
9. Delay-aligned mixing
10. Output

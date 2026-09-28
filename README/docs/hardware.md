# Hardware Documentation

## 4-Microphone Array
Four synchronized MEMS microphones provide multi-channel acoustic capture for event processing and direction estimation.

## ADC / Codec
Provides multi-channel sampling and analog-to-digital conversion.

## Fast Limiter Path
Prototype blocks:
1. Mic preamp
2. Diode clipper/protection
3. VCA/compressor
4. Buffer/protection
5. Fast ADC/digitization

Purpose: provide a low-latency protective path independent of AI decisions.

## Embedded Compute
Target architecture: Raspberry Pi Compute Module-class platform with an edge AI accelerator.

## Output
Delay-aligned mixer → DAC + amplifier → single tactical headset.

## Hardware Validation Checklist
- [ ] Microphone synchronization
- [ ] ADC/codec channel verification
- [ ] Fast-path latency measurement
- [ ] AI-path latency measurement
- [ ] Mixer delay alignment
- [ ] DAC output verification
- [ ] Fail-safe testing
- [ ] Power/thermal testing
- [ ] EMI/EMC testing

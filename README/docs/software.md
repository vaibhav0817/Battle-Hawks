# Software Documentation

## Processing Pipeline
1. Audio acquisition
2. Pre-processing
3. Acoustic event classification
4. Decision engine
5. Priority engine
6. Adaptive DSP
7. GCC-PHAT localization
8. HRTF spatial rendering
9. Delay-aligned mixing
10. Output

## Decision Logic
```text
Detection → Confidence → Decision → Priority
                                  ├→ Critical: preserve + protective limiting
                                  ├→ Important: enhance/preserve
                                  └→ Background: suppress/reduce
```

Keep thresholds in configuration files so experiments are reproducible.

## Dashboard
The dashboard is a development/validation console, not a replacement for the final embedded headset interface.

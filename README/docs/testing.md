# Testing and Validation

## Classification
Use a held-out test set and report accuracy, precision, recall, macro F1, weighted F1, confusion matrix and per-class results.

## SNR Gain
For a defined clean/noisy pair:
`SNR gain = processed SNR - input SNR`

Document how speech/noise segments are selected.

## STOI
Evaluate speech intelligibility using reference and processed speech. Report test-set mean and variation where possible.

## Latency
Measure multiple runs. Report mean, median and p95/worst-case where appropriate. Separate AI inference, fast-path and end-to-end latency.

## Localization
Use known source angles and report absolute angle error and front/left/right classification where applicable.

## Reproducibility
Record hardware, software version, model checkpoint, sample rate, dataset, configuration and date.

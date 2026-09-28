# AI Model Documentation

## Objective
Recognize acoustic events in noisy environments so downstream logic can decide how each event should be treated.

## Document the Exact Experiment
For every final checkpoint record:
- Base architecture
- Dataset and version
- Number of classes
- Train/validation/test split
- Augmentation
- Training configuration
- Loss function
- Checkpoint
- Quantization method

## Edge Deployment
```text
Trained Model
   ↓
Validation
   ↓
ONNX / Deployment Format
   ↓
INT8 Quantization
   ↓
Accelerator Compilation
   ↓
Embedded Inference
```

Only claim accelerator deployment after the model has been tested on the target accelerator.

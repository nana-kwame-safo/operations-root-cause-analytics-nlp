# Model Card: Aviation Demonstration Domain

## Model Overview

- Project: Operations Root Cause Analytics with NLP
- Model name: TF-IDF + One-vs-Rest Logistic Regression (Aviation Demo)
- Task: multi-label root-cause-related factor classification
- Domain: aviation incident narratives (first demonstration dataset)
- Output type: contributory-factor indicator labels with confidence scores

## Intended Use

- Incident narrative analysis in operations analytics workflows
- Root cause analysis support through confidence-aware factor indicators
- Analyst triage and review prioritization in a human-in-the-loop process

## Non-Intended Use

- Definitive root cause determination or causal proof
- Replacement for expert incident investigation
- Certified operational safety decision automation
- Autonomous investigation or enforcement workflows

## Model Architecture

- Vectorizer: TF-IDF
  - `ngram_range=(1, 2)`
  - `max_features=30000`
  - `min_df=2`
  - `strip_accents="unicode"`
  - `sublinear_tf=True`
- Classifier: One-vs-Rest Logistic Regression
  - `C=2.0`
  - `max_iter=400`
  - `class_weight="balanced"`
  - `solver="liblinear"`
  - `random_state=42`
- Persistence: `joblib` artifact export and load

## Features

- Free-text incident narrative input
- Multi-label anomaly-factor output
- Confidence scoring per predicted label
- Threshold-aware review flags
- Explainability-lite cue terms derived from linear feature contributions

## Labels

- Label count: `22`
- Label set: `Anomaly_1` through `Anomaly_22`
- Domain mappings: `app/domains/aviation/label_mapping.json`

## Threshold

- Default inference threshold: `0.50`
- Behavior:
  - suppress labels below threshold
  - return low-confidence review messaging when signal quality is borderline or mixed

## Metrics

- Micro-F1: `0.658`
- Macro-F1: `0.630`
- Samples-F1: `0.654`
- Hamming Loss: `0.073`

## Known Limitations

- Domain-specific to the aviation demonstration dataset snapshot
- Sensitive to vocabulary shift and report-style variation
- Explanation cues are approximation signals, not definitive causal attributions
- Performance may vary by rare labels and limited class representation

## Class Imbalance Concerns

The label space is imbalanced. `class_weight="balanced"` helps reduce skew impact but does not remove minority-label error risk. Analysts should pay extra attention to low-frequency label outputs and review flags.

## Responsible-Use Statement

Use outputs as analyst decision-support signals only. Predictions indicate likely root-cause-related factors and should always be reviewed in operational context by qualified personnel.

## Future Model Improvements

- Probability calibration for improved confidence interpretation
- Domain-adaptive retraining for new operational narrative sources
- More robust minority-label handling and calibration by label
- Richer per-instance explainability methods and evaluation

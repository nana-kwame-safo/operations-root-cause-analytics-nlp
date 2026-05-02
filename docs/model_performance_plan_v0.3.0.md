# v0.3.0 Model Performance Improvement Plan

## Purpose

v0.3.0 focuses on improving model evaluation quality and identifying practical performance improvements for the aviation model without replacing the current live baseline prematurely.

The current live model remains:

- TF-IDF vectorization
- One-vs-Rest Logistic Regression
- 22 aviation labels (`Anomaly_1` to `Anomaly_22`)
- Explainable coefficient-based evidence terms

## Current Full-Dataset Baseline

Current full-dataset model metrics:

| Metric | Value |
|---|---:|
| Micro-F1 | 0.7175 |
| Macro-F1 | 0.6414 |
| Samples-F1 | 0.7194 |
| Hamming loss | 0.0620 |

## Current Tooling

Existing scripts:

- `scripts/train_aviation.py` trains and writes model artifacts from a single CSV or split text/label files.
- `scripts/evaluate_aviation.py` evaluates an existing artifact on labeled local data.
- `scripts/export_aviation_artifacts.py` supports artifact copy/export and train-and-export workflows.
- `scripts/aviation_artifact_utils.py` holds the shared TF-IDF, Logistic Regression, training, metadata, and aggregate evaluation logic.

Current limitation:

- Evaluation is aggregate-first. It does not yet produce per-label precision/recall/F1, weakest-label tables, threshold tuning reports, calibration diagnostics, or structured error-analysis outputs.

## Success Targets

The v0.3.0 model work should aim to:

- Improve macro-F1 if possible, especially for weak/minority labels.
- Maintain or improve micro-F1 relative to `0.7175`.
- Reduce hamming loss below `0.0620` if possible.
- Preserve explainability through TF-IDF feature contribution scores or an equivalent analyst-facing explanation method.
- Preserve deployment compatibility with the current FastAPI response schema and `MODEL_ARTIFACT_URL` artifact loading.
- Avoid replacing the live model unless a candidate clearly improves evaluation results and responsible-use behavior.

## Work Plan

## 1) Per-Label Metrics

Add evaluation outputs for each label:

- support
- prevalence
- precision
- recall
- F1
- false positives
- false negatives

Why it matters:

- Macro-F1 is lower than micro-F1, which suggests weaker behavior on some labels.
- Per-label tables will show which labels need threshold or data/feature attention.

Proposed output:

- `outputs/evaluation/aviation_per_label_metrics.csv`
- summarized metrics in refreshed model card

## 2) Weakest-Label Analysis

Rank labels by:

- lowest F1
- lowest recall
- lowest precision
- low support / high error rate

Why it matters:

- Model improvement should target weak labels rather than only optimizing global averages.

Review questions:

- Are weak labels rare?
- Are weak labels semantically overlapping with stronger labels?
- Are weak labels driven by sparse or noisy lexical cues?

## 3) Threshold Tuning

Evaluate thresholds globally and per label.

Candidate strategies:

- current global threshold `0.50`
- global threshold search over a grid such as `0.10` to `0.90`
- per-label threshold tuning for F1 or recall-constrained review workflows

Why it matters:

- Multi-label classifiers often need threshold tuning, especially under class imbalance.
- A label-specific threshold table may improve macro-F1 without changing the model family.

Guardrail:

- Threshold tuning must not create misleading confidence behavior or excessive false positives.

## 4) Class Imbalance Review

Measure:

- positive count per label
- negative count per label
- prevalence
- co-occurrence patterns

Candidate actions:

- review current `class_weight="balanced"` behavior
- compare with unweighted Logistic Regression
- test label-specific regularization/threshold strategies
- consider sample weighting only if justified by evaluation results

Why it matters:

- Rare labels may dominate macro-F1 weakness.
- Overcorrecting imbalance can inflate false positives.

## 5) Hyperparameter Search

Run controlled searches for the current interpretable model family.

Candidate TF-IDF settings:

- `max_features`: `20000`, `30000`, `50000`
- `ngram_range`: `(1, 1)`, `(1, 2)`, `(1, 3)`
- `min_df`: `1`, `2`, `3`, `5`
- `sublinear_tf`: `true`, `false`

Candidate Logistic Regression settings:

- `C`: `0.5`, `1.0`, `2.0`, `4.0`
- `class_weight`: `balanced`, `None`
- `solver`: keep `liblinear` first for compatibility unless search shows a need to change

Why it matters:

- This can improve performance while retaining explainability and deployment simplicity.

Guardrail:

- Use held-out evaluation and avoid selecting parameters only from one lucky split.

## 6) Calibration Check

Evaluate probability quality before changing decision thresholds.

Candidate diagnostics:

- reliability curves by label where support is sufficient
- Brier score by label
- probability distribution plots for positive vs negative examples
- compare calibrated vs uncalibrated decision behavior

Candidate calibration methods:

- sigmoid/Platt-style calibration
- isotonic calibration for labels with enough support

Why it matters:

- Analyst review flags depend on confidence values.
- Better F1 with poorly calibrated scores may degrade user trust.

## 7) Error Analysis

Create structured, non-public error-analysis outputs without exposing raw narratives in committed docs.

Review categories:

- false positives with high confidence
- false negatives with high expected label support
- labels with overlapping evidence terms
- short or sparse narratives
- narratives with multiple interacting factors

Rules:

- Do not commit raw narrative text.
- Summaries can include aggregate counts, label IDs, label names, and anonymized feature-level patterns.

## 8) Updated Model Card

Update `docs/model_card_aviation.md` after model evaluation work is complete.

Include:

- current aggregate metrics
- per-label metric summary
- weakest-label findings
- threshold decision
- calibration findings
- known limitations
- deployment artifact version and hosting approach

## Candidate Promotion Criteria

A new model artifact can replace the live baseline only if it:

- improves macro-F1 or provides a clear tradeoff benefit for weak labels
- maintains or improves micro-F1
- reduces or does not worsen hamming loss
- preserves explainable outputs in the UI/API
- remains compatible with current Render + Hugging Face artifact deployment
- passes existing tests and any new evaluation checks
- keeps responsible-use framing intact

## Non-Goals for v0.3.0

- Do not replace the current live model without clear evidence.
- Do not introduce transformer deployment as the default model.
- Do not commit raw data or `model.joblib`.
- Do not treat model outputs as definitive causality.

## Expected Deliverables

- Evaluation script enhancements for per-label metrics and threshold analysis
- Generated local evaluation artifacts kept out of Git unless safe and summarized
- Updated `docs/model_card_aviation.md`
- Recommendation on whether to keep, tune, or replace the current artifact
- Optional candidate artifact uploaded externally only after review

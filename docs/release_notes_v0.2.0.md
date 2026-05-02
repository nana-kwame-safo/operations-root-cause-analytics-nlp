# v0.2.0 - Explainable Analyst Interface

This release adds an analyst-facing explainability layer to **Operations Root Cause Analytics with NLP** while preserving the current TF-IDF + One-vs-Rest Logistic Regression baseline.

## Added

- Human-readable aviation label registry for `Anomaly_1` through `Anomaly_22`
- Plain-English factor descriptions for normal users
- Technical analyst explanations for review workflows
- Evidence-term contribution scores from the TF-IDF + logistic regression coefficient method
- Highlighted text evidence spans in the incident narrative
- Simple View for quick interpretation
- Analyst View for label IDs, technical descriptions, contribution scores, model metadata, and alternative factors
- Richer `/predict` API response schema with label metadata, evidence terms, evidence spans, top scores, and model info
- Batch output with human-readable label names while retaining raw label IDs for traceability
- Updated screenshots for dark and light theme explainability views

## Retained

- Responsible-use wording: outputs are analyst-support indicators, not definitive causality findings
- Existing FastAPI endpoints and lightweight static UI approach
- External model artifact handling through `MODEL_ARTIFACT_URL`
- `model.joblib` remains externally hosted and is not committed to GitHub
- Raw data remains excluded from the repository

## Notes

The label taxonomy remains a working taxonomy derived from model features and should be validated against source documentation or expert domain review before operational use.

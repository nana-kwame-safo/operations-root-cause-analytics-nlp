# Model Improvement Roadmap

This roadmap defines the next modeling steps for **Operations Root Cause Analytics with NLP** while keeping the current live app stable.

## Baseline Principle

Keep the current **TF-IDF + One-vs-Rest Logistic Regression** model as the interpretable production baseline until candidate models are validated and operationally reviewed.

## Compatibility Guardrails

- Do not break existing endpoints (`/predict`, `/predict-batch`, `/model-info`).
- Preserve current response fields used by the UI.
- Introduce candidate models behind artifacts/config flags first.
- Promote a new default only after metric, calibration, and analyst-review checks pass.

## Planned Model Track

## 1) Interpretable Baseline (Current)

- **Approach**: TF-IDF + One-vs-Rest Logistic Regression with evidence-term contributions.
- **Useful when**: transparency, fast iteration, and analyst explainability are primary requirements.
- **Status**: active baseline.

## 2) Full Dataset Retraining

- **Approach**: retrain baseline model on the full permitted aviation dataset snapshot.
- **Useful when**: current artifact was trained on subset/demo-scale data and broader coverage is needed.
- **Expected outcome**: stronger recall/coverage and more stable label-wise behavior.

## 3) Probability Calibration

- **Approach**: calibrate classifier outputs (for example Platt scaling or isotonic strategies per label where appropriate).
- **Useful when**: raw probabilities are not reliable for threshold-based review decisions.
- **Expected outcome**: better confidence quality and better review-flag behavior.

## 4) Transformer Baseline

- **Approach**: train a transformer-based multi-label baseline for side-by-side comparison.
- **Useful when**: nonlinear semantics and context windows likely outperform sparse lexical features.
- **Expected outcome**: performance benchmark vs the interpretable baseline.

## 5) Sentence-Transformer Embedding Pipeline

- **Approach**: use sentence embeddings with lightweight multi-label classifiers or nearest-centroid/linear heads.
- **Useful when**: stronger semantic clustering is needed with simpler downstream training footprints.
- **Expected outcome**: robust semantic features and improved cross-phrase generalization.

## 6) Zero-Shot / Weakly Supervised Expansion

- **Approach**: seed candidate labels or domains using weak supervision and zero-shot labeling workflows.
- **Useful when**: expanding to new domains with limited curated labels.
- **Expected outcome**: faster domain bootstrapping before full supervised retraining.

## 7) SHAP/LIME Explainability Comparison

- **Approach**: compare current coefficient-based explanations with SHAP/LIME for selected candidate models.
- **Useful when**: model class changes reduce interpretability of linear coefficients.
- **Expected outcome**: explainability quality benchmarks and analyst trust comparisons.

## 8) Similar-Case Retrieval

- **Approach**: add retrieval of nearest historical narratives (embedding or sparse retrieval) as supporting context.
- **Useful when**: analysts need precedent-based review support and traceability.
- **Expected outcome**: better human review efficiency and contextual confidence checks.

## 9) Analyst Feedback Loop

- **Approach**: capture analyst feedback (`useful`, `not useful`, `needs review`, `wrong factor`) for evaluation/retraining data.
- **Useful when**: improving taxonomy quality and closing model-to-operations feedback cycles.
- **Expected outcome**: continuous quality improvement and clearer governance trail.

## 10) Multimodal Extension

- **Approach**: combine text with attachments/log references (images, PDFs, sensor/event logs) using multimodal-ready schemas.
- **Useful when**: non-text evidence materially affects interpretation.
- **Expected outcome**: higher-fidelity incident assessment support.

## 11) Agentic Analyst-Support Workflows

- **Approach**: orchestrate guided triage, case summarization, and structured follow-up recommendations with human oversight.
- **Useful when**: analyst queues are high-volume and workflow orchestration is needed.
- **Expected outcome**: faster analyst throughput with auditable human-in-the-loop controls.

## Risk Register and Controls

## Overfitting

- **Risk**: high offline scores with weak generalization.
- **Control**: strict holdout strategy, cross-validation checks, and domain-shift testing.

## Class Imbalance

- **Risk**: minority factors are under-detected.
- **Control**: per-label metrics, class weighting, threshold tuning, and targeted error analysis.

## Poor Calibration

- **Risk**: misleading confidence values and unstable review flags.
- **Control**: calibration diagnostics (reliability curves/Brier-style checks) and post-calibration threshold review.

## Misleading Explanations

- **Risk**: explanation cues interpreted as causal proof.
- **Control**: keep explicit caveats, compare explanation methods, and retain analyst validation requirement.

## False Sense of Causality

- **Risk**: users over-interpret model outputs as definitive root cause.
- **Control**: enforce responsible-use wording in UI/docs and keep review-flag workflow mandatory for decisions.

## Exit Criteria Before Baseline Replacement

- Candidate model beats or matches baseline on micro/macro/samples F1 and hamming loss.
- Calibration quality is improved or at least not degraded.
- Explainability remains usable for analyst review support.
- No regression in API/UI compatibility.
- Responsible-use and governance checks are updated with the new model behavior.

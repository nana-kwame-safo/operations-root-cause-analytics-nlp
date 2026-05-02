# Public Roadmap

This roadmap summarizes planned release increments for **Operations Root Cause Analytics with NLP**.

Detailed model track and risk controls: [docs/model_roadmap.md](model_roadmap.md)

## v0.1.0 - ASRS Text-Based MVP

- FastAPI endpoints for health, domains, model info, single prediction, and batch prediction
- Lightweight analyst UI for narrative scoring and CSV batch workflows
- TF-IDF + One-vs-Rest Logistic Regression aviation baseline
- Confidence-ranked root-cause-related factor indicators with review flags
- Responsible-use framing for analyst review support

## v0.2.0 - Explainable Analyst Interface

- Human-readable label registry for aviation factor indicators
- Simple View and Analyst View in the UI
- Evidence-term contribution scoring and highlighted narrative spans
- Enhanced prediction summary cards and alternative-factor analysis table
- Feedback-capture workflow scaffolding for analyst teams

## v0.3.0 - Full Dataset Model Refinement

- Training on the full permitted aviation dataset snapshot
- Probability calibration and thresholding updates for confidence-aware review behavior
- Expanded evaluation artifacts and refreshed model card documentation
- Improved label descriptions from broader validation evidence

## v0.4.0 - Model Comparison and Transformer Baseline

- Side-by-side evaluation of linear baseline vs transformer candidate models
- Sentence-transformer embedding baseline for semantic comparison
- SHAP/LIME explainability comparison against coefficient-based explanations
- Shared evaluation harness for metrics and error-pattern analysis
- Tradeoff documentation for performance, transparency, and operational fit
- Recommendation package for next production-style prototype baseline

## v0.5.0 - Expansion and Retrieval

- Zero-shot or weakly supervised expansion workflow for new domains
- Similar-case retrieval support for analyst context and traceability
- Analyst feedback loop integration for iterative model improvement

## v0.6.0 - Multimodal and Agentic Analyst-Support Workflows

- Multimodal-ready ingestion for text plus attachment references (images, PDFs, logs)
- Analyst-assistant workflow orchestration for triage and follow-up
- Structured review-state tracking and handoff prompts
- Case summarization and investigation support scaffolding
- Governance controls for role-aware, auditable assistant actions

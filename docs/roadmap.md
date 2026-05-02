# Public Roadmap

This roadmap summarizes planned release increments for **Operations Root Cause Analytics with NLP**.

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
- Updated calibration, thresholding, and confidence behavior checks
- Expanded evaluation artifacts and refreshed model card documentation
- Improved label descriptions from broader validation evidence

## v0.4.0 - Model Comparison and Transformer Baseline

- Side-by-side evaluation of linear baseline vs transformer candidate models
- Shared evaluation harness for metrics and error-pattern analysis
- Tradeoff documentation for performance, transparency, and operational fit
- Recommendation package for next production-style prototype baseline

## v0.5.0 - Multimodal Inputs

- Data contracts for linking narratives with attachment references (images, PDFs, logs)
- Pipeline updates for multimodal-ready ingestion and traceability
- UI and API updates for evidence-link visualization
- Responsible-use extensions for multimodal evidence interpretation

## v0.6.0 - Agentic Analyst-Support Workflows

- Analyst-assistant workflow orchestration for triage and follow-up
- Structured review-state tracking and handoff prompts
- Case summarization and investigation support scaffolding
- Governance controls for role-aware, auditable assistant actions

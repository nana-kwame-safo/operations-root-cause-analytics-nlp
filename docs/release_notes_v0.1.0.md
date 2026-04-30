# Release Notes v0.1.0

## Tag
`v0.1.0`

## Title
Initial MVP — Operations Root Cause Analytics with NLP

## Summary
First public MVP release of **Operations Root Cause Analytics with NLP**, framed as an operations analytics system for confidence-aware incident narrative factor classification with analyst review support.

## Included in This Release

- FastAPI backend with endpoints:
  - `GET /health`
  - `GET /domains`
  - `GET /model-info`
  - `POST /predict`
  - `POST /predict-batch`
- Single narrative prediction workflow
- Batch CSV prediction workflow
- ASRS aviation incident report demonstration domain
- Confidence-aware thresholding and top-k filtering for root-cause-related factor predictions
- Analyst review flags for low-confidence or no-strong-signal cases
- Explainability-lite cue terms
- Model metadata endpoint and model/domain configuration scaffolding
- Lightweight web UI (Operations RCA NLP)
- Docker support (`Dockerfile`, `.dockerignore`)
- Test suite with pytest and GitHub Actions workflow
- Evidence-backed README with visuals, results summary, and operational references
- Responsible-use, data statement, model card, and future domain documentation
- Multi-domain foundation and multimodal-ready roadmap framing

## Notes

- This release is a decision-support prototype and does not perform definitive root cause determination.
- Raw incident dataset files are intentionally excluded from the public repository.
- Local model artifacts are required for live predictions.

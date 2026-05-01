# Release Notes v0.1.0

## Title
Initial MVP — Operations Root Cause Analytics with NLP

## Summary
First public MVP release of **Operations Root Cause Analytics with NLP** for operations intelligence workflows using root-cause-related factor classification and analyst review support.

## Included in This Release

- FastAPI backend
- Lightweight web UI
- ASRS aviation demonstration domain
- Single narrative scoring
- Batch CSV scoring
- Confidence-aware thresholding
- Root-cause-related factor predictions
- Explanation cues
- Analyst review flags
- Model metadata endpoint
- Docker support
- `pytest` suite
- Evidence-backed README
- Responsible-use documentation
- Architecture and workflow visuals
- Multi-domain and multimodal-ready roadmap

## API Surface in v0.1.0

- `GET /health`
- `GET /domains`
- `GET /model-info`
- `POST /predict`
- `POST /predict-batch`

## Notes

- This release is a decision-support prototype and does not establish definitive causality findings.
- Raw incident dataset files are intentionally excluded from the public repository.
- Live prediction endpoints require local or deployment-attached `artifacts/aviation/model.joblib`.

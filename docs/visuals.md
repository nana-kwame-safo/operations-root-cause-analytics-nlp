# Visual Assets Guide

This file documents what each public visual shows, how it was produced, and how to replace it before future releases.

## Visual Inventory

| File | What it shows | Visual type | Current status |
|---|---|---|---|
| `docs/images/app_home.png` | Main analyst UI (home, controls, narrative input) | Real app screenshot | Release-ready |
| `docs/images/prediction_result.png` | Predicted labels, confidence scores, explanation cues, review flag | Real app screenshot | Release-ready |
| `docs/images/batch_scoring.png` | CSV upload workflow and structured batch output view | Real app screenshot | Release-ready |
| `docs/images/architecture.png` | End-to-end project architecture (UI -> API -> services -> artifacts -> outputs) | Generated diagram | Release-ready |
| `docs/images/model_workflow.png` | NLP inference workflow from narrative text to structured output | Generated diagram | Release-ready |
| `docs/images/metrics_summary.png` | Aviation baseline metrics (Micro-F1, Macro-F1, Samples-F1, Hamming Loss) | Generated chart | Release-ready |

Temporary mock visuals are not used in the current README.

## Regenerate Diagrams and Metrics Visual

Run:

```bash
python scripts/generate_docs_visuals.py
```

This regenerates:

- `docs/images/architecture.png`
- `docs/images/model_workflow.png`
- `docs/images/metrics_summary.png`

## Refresh Real UI Screenshots

1. Start the app:
   ```bash
   uvicorn app.main:app --reload
   ```
2. Capture the required pages:
   - `http://127.0.0.1:8000` -> `docs/images/app_home.png`
   - `http://127.0.0.1:8000/?demo=prediction&view=prediction` -> `docs/images/prediction_result.png`
   - `http://127.0.0.1:8000/?demo=batch&view=batch` -> `docs/images/batch_scoring.png`
3. Use consistent dimensions (recommended width `1600px`) and crop only if readability improves.

## Pre-Release Visual Checks

Run:

```bash
grep -n "docs/images/" README.md
grep -Rni --exclude-dir=.git "PLACEHOLDER\\|placeholder" README.md docs/images || true
```

Confirm:

- Every README visual path resolves.
- No README visual contains placeholder text.
- The architecture and workflow diagrams match the current system design.

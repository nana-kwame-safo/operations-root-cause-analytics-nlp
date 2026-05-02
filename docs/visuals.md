# Visual Assets Guide

This file documents what each public visual shows, how it was produced, and how to replace it before future releases.

## Visual Inventory

| File | What it shows | Visual type | Current status |
|---|---|---|---|
| `docs/images/app_home_dark.png` | Main analyst UI (home, controls, narrative input) in dark theme | Live UI screenshot | Release-ready |
| `docs/images/app_home_light.png` | Main analyst UI (home, controls, narrative input) in light theme | Live UI screenshot | Release-ready |
| `docs/images/prediction_result_dark.png` | Single-report prediction results in dark theme | Live UI screenshot | Release-ready |
| `docs/images/prediction_result_light.png` | Single-report prediction results in light theme | Live UI screenshot | Release-ready |
| `docs/images/batch_scoring_dark.png` | Batch CSV scoring workflow in dark theme | Live UI screenshot | Release-ready |
| `docs/images/batch_scoring_light.png` | Batch CSV scoring workflow in light theme | Live UI screenshot | Release-ready |
| `docs/images/explainable_prediction_dark.png` | Explainable prediction Simple View with human-readable label names in dark theme | Live UI screenshot | Release-ready |
| `docs/images/explainable_prediction_light.png` | Explainable prediction Simple View with human-readable label names in light theme | Live UI screenshot | Release-ready |
| `docs/images/analyst_view_dark.png` | Analyst View with technical explanation, contribution scores, and alternatives in dark theme | Live UI screenshot | Release-ready |
| `docs/images/analyst_view_light.png` | Analyst View with technical explanation, contribution scores, and alternatives in light theme | Live UI screenshot | Release-ready |
| `docs/images/evidence_highlighting_dark.png` | Highlighted narrative evidence spans in dark theme | Live UI screenshot | Release-ready |
| `docs/images/evidence_highlighting_light.png` | Highlighted narrative evidence spans in light theme | Live UI screenshot | Release-ready |
| `docs/images/model_info_available.png` | Model information panel with `artifact_status: available` | Live UI screenshot | Optional; capture when needed |
| `docs/images/app_home.png` | Previous home screenshot retained for compatibility | Live UI screenshot | Legacy snapshot |
| `docs/images/prediction_result.png` | Previous prediction screenshot retained for compatibility | Live UI screenshot | Legacy snapshot |
| `docs/images/batch_scoring.png` | Previous batch screenshot retained for compatibility | Live UI screenshot | Legacy snapshot |
| `docs/images/architecture.png` | End-to-end project architecture (UI -> API -> services -> artifacts -> outputs) | Generated diagram | Release-ready |
| `docs/images/model_workflow.png` | NLP inference workflow from narrative text to structured output | Generated diagram | Release-ready |
| `docs/images/metrics_summary.png` | Aviation baseline metrics (Micro-F1, Macro-F1, Samples-F1, Hamming Loss) | Generated chart | Release-ready |

The following optional screenshot is not currently present in this repository:

- `docs/images/model_info_available.png`

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
   - `http://127.0.0.1:8000/?theme=dark` -> `docs/images/app_home_dark.png`
   - `http://127.0.0.1:8000/?theme=light` -> `docs/images/app_home_light.png`
   - `http://127.0.0.1:8000/?demo=prediction&view=prediction&theme=dark` -> `docs/images/prediction_result_dark.png`
   - `http://127.0.0.1:8000/?demo=prediction&view=prediction&theme=light` -> `docs/images/prediction_result_light.png`
   - `http://127.0.0.1:8000/?demo=batch&view=batch&theme=dark` -> `docs/images/batch_scoring_dark.png`
   - `http://127.0.0.1:8000/?demo=batch&view=batch&theme=light` -> `docs/images/batch_scoring_light.png`
   - `http://127.0.0.1:8000/?theme=dark` (scroll to model panel) -> `docs/images/model_info_available.png` (optional)
   - `http://127.0.0.1:8000/?theme=dark` after running single prediction in Simple View -> `docs/images/explainable_prediction_dark.png`
   - `http://127.0.0.1:8000/?theme=light` after running single prediction in Simple View -> `docs/images/explainable_prediction_light.png`
   - `http://127.0.0.1:8000/?theme=dark` after switching to Analyst View -> `docs/images/analyst_view_dark.png`
   - `http://127.0.0.1:8000/?theme=light` after switching to Analyst View -> `docs/images/analyst_view_light.png`
   - `http://127.0.0.1:8000/?theme=dark` with the evidence narrative card visible -> `docs/images/evidence_highlighting_dark.png`
   - `http://127.0.0.1:8000/?theme=light` with the evidence narrative card visible -> `docs/images/evidence_highlighting_light.png`
3. Optional compatibility refresh:
   - Save dark-theme home/prediction/batch variants as `app_home.png`, `prediction_result.png`, and `batch_scoring.png` if legacy references remain.
4. Use consistent dimensions (recommended width `1600px`) and crop only if readability improves.

Suggested screenshot narrative:

```text
Flight Data Recorder analysis suggests a potential intermittent fault in the Inertial Reference Unit or a momentary software glitch in the Flight Management Computer leading to erroneous sensor data. The aircraft was removed from service for further troubleshooting.
```

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

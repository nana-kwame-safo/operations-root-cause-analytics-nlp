# Visual Assets Guide

This document tracks which README visuals are runtime screenshots vs generated diagrams, and how to regenerate them for future releases.

## Visual Inventory

| File | Type | Source | Notes |
|---|---|---|---|
| `docs/images/app_home.png` | Real screenshot | Running FastAPI UI | Captured from `http://127.0.0.1:8000` |
| `docs/images/prediction_result.png` | Real screenshot | Running FastAPI UI | Captured from app demo state (`?demo=prediction&view=prediction`) |
| `docs/images/batch_scoring.png` | Real screenshot | Running FastAPI UI | Captured from app demo state (`?demo=batch&view=batch`) |
| `docs/images/architecture.png` | Diagram | Generated image | Left-to-right architecture flow |
| `docs/images/model_workflow.png` | Diagram | Generated image | Narrative-to-output ML workflow |
| `docs/images/metrics_summary.png` | Metrics chart | Generated image | Uses aviation demo metrics in README/model card |

## Regenerate Generated Visuals

Run:

```bash
python scripts/generate_docs_visuals.py
```

This command regenerates:

- `docs/images/architecture.png`
- `docs/images/model_workflow.png`
- `docs/images/metrics_summary.png`

## Capture/Replace Real UI Screenshots

1. Start the app:
   ```bash
   uvicorn app.main:app --reload
   ```
2. Open and capture the desired state:
   - `http://127.0.0.1:8000` (home)
   - `http://127.0.0.1:8000/?demo=prediction&view=prediction` (single prediction result state)
   - `http://127.0.0.1:8000/?demo=batch&view=batch` (batch scoring state)
3. Save to:
   - `docs/images/app_home.png`
   - `docs/images/prediction_result.png`
   - `docs/images/batch_scoring.png`
4. Keep images clear and consistent (recommended width around `1600px`).

## Pre-Release Checks

- Ensure no README image contains the word `placeholder`.
- Ensure README paths resolve under `docs/images/`.
- Re-check references after edits:
  ```bash
  grep -n "docs/images/" README.md
  ```

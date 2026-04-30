# AGENTS.md

## Project Overview
Operations Root Cause Analytics with NLP (short name: Operations RCA NLP) is an operations intelligence NLP system for classifying incident narratives into likely root-cause-related factor categories for analyst review support. Aviation (ASRS/SIAM) is the first implemented demonstration domain.

## Run Commands

### Run app
```bash
uvicorn app.main:app --reload
```

### Run tests
```bash
pytest -q
```

### Build and run Docker image
```bash
docker build -t operations-root-cause-analytics-nlp .
docker run -p 8000:8000 operations-root-cause-analytics-nlp
```

## Data Handling Rules
- Do not commit raw data files.
- Keep `data/raw`, `data/interim`, and `data/processed` out of version control.

## Framing Guardrail
- Do not frame outputs as definitive root-cause determination.
- Describe outputs as root-cause-related, contributory-factor, or anomaly-factor indicators for analyst review.

## Preferred Code Style
- Small modular services
- Typed Pydantic schemas
- Clear error handling and explicit metadata
- No hardcoded absolute paths

## Expected Repo Structure
- `app/` backend + UI
- `artifacts/` local model placeholders/examples
- `scripts/` training/evaluation/export tools
- `docs/` model/data/responsible-use/architecture notes
- `tests/` pytest suite

## Done Criteria
1. API routes work (`/health`, `/domains`, `/model-info`, `/predict`, `/predict-batch`).
2. UI can run single and batch workflows.
3. Missing artifacts fail gracefully with clear guidance.
4. Tests pass.
5. Docker build runs.
6. Docs reflect operations analytics framing and responsible-use constraints.

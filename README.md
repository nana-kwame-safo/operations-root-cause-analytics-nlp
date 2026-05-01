# Operations Root Cause Analytics with NLP

**Natural Language Processing for Incident Narrative Analysis and Root Cause Factor Classification**

Operations RCA NLP is an operations intelligence NLP project for root-cause-related factor classification and analyst review support from free-text incident narratives.

Short name: **Operations RCA NLP**  
Repository: **operations-root-cause-analytics-nlp**

## Live Demo

Try the live app here: [Operations RCA NLP Demo](PASTE_RENDER_URL_HERE)

> This demo supports root-cause-related factor classification for analyst review. It does not establish definitive causality or replace expert investigation.
>
> Note: The public deployment may show model artifact status as missing until the aviation model artifact is generated and attached to the deployment environment. The API, UI, metadata, and documentation are live; full prediction requires `artifacts/aviation/model.joblib`.

## Demo Preview

![App Home Screenshot](docs/images/app_home.png)
_Real screenshot of the running UI home view._

![Prediction Result View](docs/images/prediction_result.png)
_Real screenshot of single-report prediction output._

![Batch Scoring View](docs/images/batch_scoring.png)
_Real screenshot of batch CSV scoring workflow._

Visual asset notes and replacement instructions: [docs/visuals.md](docs/visuals.md)

## Project Background

Operations teams generate high volumes of free-text incident narratives across safety logs, maintenance events, disruption reports, and near-miss records. These narratives contain contributory-factor indicators, but manual review is hard to scale consistently. This project converts narrative text into structured outputs for analyst review support and downstream operations intelligence workflows.

## Why This Matters

- Faster triage for analyst teams handling large incident queues
- Better detection of recurring contributory-factor patterns
- More consistent categorization across reviewers and time periods
- Dashboard-ready outputs for operational reporting and action tracking
- Practical support for root-cause-related analysis workflows

## Evidence-Backed Motivation

- NASA's Aviation Safety Reporting System (ASRS) has collected and analyzed over 2 million safety reports since 1976, showing the scale and value of narrative safety data. [1]
- ASRS submissions include unsafe occurrences, near-misses, hazardous situations, and best-practice observations, making aviation a strong first demonstration domain. [1][2]
- OSHA incident-investigation guidance emphasizes finding and correcting underlying causes to prevent recurrence. [3]
- FAA SMS guidance describes hazard identification, risk assessment, risk analysis, and risk control as core safety risk management activities. [4]
- NIST AI RMF 1.0 highlights role clarity and governance when AI outputs support human decision workflows. [5]

## What the System Does

- Accepts free-text incident narratives
- Applies text preprocessing and TF-IDF vectorisation
- Predicts multi-label root-cause-related factor categories
- Returns confidence scores and explanation cues
- Applies threshold filtering and analyst review flags
- Supports both single narrative scoring and CSV batch scoring
- Exposes outputs through FastAPI endpoints and a lightweight web UI

Current positioning:

- ASRS aviation incident reports are the first implemented demonstration domain
- The platform is not aviation-only and is designed for multi-domain onboarding
- The MVP is text-based now
- The architecture is multi-domain-ready
- The roadmap is multimodal-ready later
- Agentic analyst-support workflows are planned as a future direction

## System Architecture Diagram

![Architecture Diagram](docs/images/architecture.png)
_Project-specific architecture from user input to analyst outputs and dashboard-ready results._

## Model Workflow Diagram

![Model Workflow Diagram](docs/images/model_workflow.png)
_Inference workflow from incident narrative through preprocessing, classification, filtering, and structured output._

## Results Summary

![Metrics Summary](docs/images/metrics_summary.png)
_Aviation demonstration metrics overview._

| Metric | Value |
|---|---:|
| Micro-F1 | 0.658 |
| Macro-F1 | 0.630 |
| Samples-F1 | 0.654 |
| Hamming Loss | 0.073 |

Notes:

- Metrics are from the aviation demonstration domain baseline.
- New domains require domain-specific retraining and validation.
- Detailed context: [docs/model_card_aviation.md](docs/model_card_aviation.md)

## Example Output

```json
{
  "input_text": "Crew received conflicting altitude and approach instructions during descent.",
  "domain": "aviation",
  "predicted_labels": [
    {
      "label": "Anomaly_2",
      "score": 0.81,
      "explanation_terms": ["altitude", "approach", "clearance"]
    },
    {
      "label": "Anomaly_19",
      "score": 0.64,
      "explanation_terms": ["communication", "controller", "instruction"]
    }
  ],
  "threshold_used": 0.5,
  "review_flag": false,
  "message": "Predictions generated successfully."
}
```

The output is a confidence-ranked set of contributory-factor indicators for analyst review support, not definitive causality findings.

## API Endpoints

- `GET /health`
- `GET /domains`
- `GET /model-info`
- `POST /predict`
- `POST /predict-batch`

### cURL Examples

`GET /health`
```bash
curl -X GET "http://127.0.0.1:8000/health"
```

`GET /domains`
```bash
curl -X GET "http://127.0.0.1:8000/domains"
```

`GET /model-info`
```bash
curl -X GET "http://127.0.0.1:8000/model-info"
```

`POST /predict`
```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Crew received conflicting altitude and approach clearance instructions during descent.",
    "domain": "aviation",
    "threshold": 0.5,
    "top_k": 5
  }'
```

`POST /predict-batch`
```bash
curl -X POST "http://127.0.0.1:8000/predict-batch" \
  -F "file=@sample_inputs/aviation_batch_reports.csv" \
  -F "domain=aviation" \
  -F "threshold=0.5" \
  -F "top_k=5" \
  -F "text_column=text"
```

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` in your browser.

## Artifact Generation

The public repository does not include raw datasets or `model.joblib`. Generate artifacts locally from your permitted dataset copy.

Single-CSV workflow:
```bash
python scripts/train_aviation.py \
  --input-csv <local_labeled_data.csv> \
  --text-column text \
  --output-dir artifacts/aviation

python scripts/evaluate_aviation.py \
  --input-csv <local_labeled_data.csv> \
  --text-column text \
  --artifact-path artifacts/aviation/model.joblib
```

Split-file workflow (`TrainingData.txt` + `TrainCategoryMatrix.csv`):
```bash
python scripts/export_aviation_artifacts.py \
  --train-text data/raw/TrainingData.txt \
  --train-labels data/raw/TrainCategoryMatrix.csv \
  --output-dir artifacts/aviation
```

Copy pre-generated artifacts from another local folder:
```bash
python scripts/export_aviation_artifacts.py \
  --source-dir <artifact_source_dir> \
  --output-dir artifacts/aviation
```

Expected runtime files:

- `artifacts/aviation/model.joblib` (required for live predictions)
- `artifacts/aviation/metadata.json` (recommended)
- `artifacts/aviation/label_mapping.json` (optional)

## Model Artifact Handling

`model.joblib` is intentionally not committed to this public repository.

For deployment environments (including Render), you can provide an external artifact URL through:

- `MODEL_ARTIFACT_URL`

Behavior:

- If `artifacts/aviation/model.joblib` already exists, the app uses it directly.
- If it is missing and `MODEL_ARTIFACT_URL` is set, the app attempts to download the artifact to `artifacts/aviation/model.joblib` on first model load.
- If download fails, the app remains available (`/health`, `/domains`, `/model-info`, UI), and prediction endpoints continue to return model-unavailable messaging until the artifact is available.

### Render Deployment Notes

Set these environment variables in Render:

- `PYTHON_VERSION=3.11.9`
- `MODEL_ARTIFACT_URL=<https URL to your model.joblib>`

## Docker

```bash
docker build -t operations-root-cause-analytics-nlp .
docker run -p 8000:8000 operations-root-cause-analytics-nlp
```

## Responsible Use

- Decision-support system for analyst review workflows
- Not a source of definitive causality findings
- Not a replacement for expert investigation workflows
- Human review remains required
- Not certified as a production safety-critical decision system

## Roadmap

Public roadmap: [docs/roadmap.md](docs/roadmap.md)

- `v0.1.0` ASRS text-based MVP
- `v0.2.0` analytics/dashboard layer
- `v0.3.0` multi-domain expansion
- `v0.4.0` multimodal-ready expansion
- `v0.5.0` agentic analyst-support workflows

Domain onboarding guide: [docs/adding_new_domain.md](docs/adding_new_domain.md)

## Analytics Industry Relevance

This pattern supports operations intelligence teams that rely on unstructured text but need structured outputs for triage, reporting, and action tracking. It is relevant to aviation, transport, facilities, utilities, housing operations, manufacturing, and service operations where incident narratives are operationally significant.

## References

1. NASA. *Aviation Safety Reporting System (ASRS) Overview*.  
   https://www.nasa.gov/human-systems-integration-division/aviation-safety-reporting-system-overview/
2. NASA ASRS. *Database Overview*.  
   https://asrs.arc.nasa.gov/search/database.html
3. OSHA. *Incident Investigation*.  
   https://www.osha.gov/incident-investigation
4. FAA. *Safety Management System (SMS) Components*.  
   https://www.faa.gov/about/initiatives/sms/explained/components
5. NIST. *AI Risk Management Framework (AI RMF 1.0)*.  
   https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf

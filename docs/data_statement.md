# Data Statement

## Aviation Incident Report Dataset Provenance

The aviation demonstration domain is based on a local frozen NASA ASRS/SIAM 2007 benchmark snapshot used for prototype benchmarking and evaluation.

## Local Frozen Snapshot Note

The training/evaluation setup assumes a user-managed local dataset snapshot. This repository does not include the original benchmark records and does not guarantee source-hosted reproducibility without local data access.

## Public Repository Data Exclusion Policy

- Raw incident records are excluded from this public repository.
- No source narrative corpus files are committed.
- No personally identifying or sensitive incident data should be committed.

## Artifact Generation Guidance

Generate model artifacts locally from your permitted dataset copy:

1. Train/export demo model from a single labeled CSV:
   - `python scripts/train_aviation.py --input-csv <local_labeled_data.csv> --text-column text --output-dir artifacts/aviation`
2. Train/export demo model from split files (`TrainingData.txt` + `TrainCategoryMatrix.csv`):
   - `python scripts/export_aviation_artifacts.py --train-text data/raw/TrainingData.txt --train-labels data/raw/TrainCategoryMatrix.csv --output-dir artifacts/aviation`
3. Evaluate artifact against labeled local data:
   - `python scripts/evaluate_aviation.py --input-csv <local_labeled_data.csv> --text-column text --artifact-path artifacts/aviation/model.joblib`
4. Copy previously generated artifacts into repo artifact directory:
   - `python scripts/export_aviation_artifacts.py --source-dir <artifact_source_dir> --output-dir artifacts/aviation`

### Input Format Notes

- Single-CSV mode expects one text column (default `text`) plus label columns (`Anomaly_1` to `Anomaly_22`).
- Split-file mode expects:
  - a text file (`.txt`) with one narrative per line or a CSV containing the text column
  - a label matrix CSV containing `Anomaly_*` columns
- If your local labels use different column names, map/rename to `Anomaly_*` before training.

Expected runtime artifact files:
- `artifacts/aviation/model.joblib` (required for predictions)
- `artifacts/aviation/metadata.json` (recommended)
- `artifacts/aviation/label_mapping.json` (optional)

## Data Limitations

- The aviation sample is a demonstration dataset, not a complete representation of all operational incident narratives.
- Label definitions and class balance may not transfer to other operational domains without re-annotation and retraining.
- Narrative quality, reporting style, and vocabulary variation can affect model behavior.

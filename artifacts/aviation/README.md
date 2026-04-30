# Aviation Artifacts

Place generated local artifacts for the aviation demonstration domain in this folder.

Expected files:

- `model.joblib` (required for prediction endpoints)
- `metadata.json` (recommended)
- `label_mapping.json` (optional if labels are embedded in metadata/artifact)

Do not commit raw incident datasets in this repository.

Generate artifacts locally from a labeled CSV:
```bash
python scripts/train_aviation.py \
  --input-csv <local_labeled_data.csv> \
  --text-column text \
  --output-dir artifacts/aviation
```

Generate artifacts locally from split files:
```bash
python scripts/export_aviation_artifacts.py \
  --train-text data/raw/TrainingData.txt \
  --train-labels data/raw/TrainCategoryMatrix.csv \
  --output-dir artifacts/aviation
```

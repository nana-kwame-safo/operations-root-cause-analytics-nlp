# Domain Artifact Template

Use this folder as a template when onboarding a new narrative domain.

Expected runtime artifacts for `artifacts/<domain_id>/`:

- `model.joblib` (required for prediction)
- `metadata.json` (recommended)
- `label_mapping.json` (optional if labels are embedded in artifact metadata)

Do not commit raw datasets or sensitive source records.

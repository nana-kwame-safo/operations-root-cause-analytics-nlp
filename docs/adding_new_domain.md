# Adding a New Domain

This project is designed for multi-domain operational narrative analytics. Aviation is the first implemented domain, but the same architecture can support additional text domains with domain-specific labels, training data, and artifact bundles.

## Domain Onboarding Checklist

1. Create domain configuration files:
   - Copy template files from `app/domains/_template/`
   - Create `app/domains/<domain_id>/domain_config.json`
   - Create `app/domains/<domain_id>/metadata.example.json`
   - Create `app/domains/<domain_id>/label_mapping.json`
2. Train and export model artifacts:
   - Generate `artifacts/<domain_id>/model.joblib`
   - Generate `artifacts/<domain_id>/metadata.json`
   - Generate `artifacts/<domain_id>/label_mapping.json` (if not embedded)
3. Register domain behavior:
   - Ensure `status` is `implemented` in the new domain config
   - Keep naming and `artifact_subdir` aligned with `artifacts/<domain_id>/`
4. Add sample inputs:
   - Add representative sample files under `sample_inputs/`
5. Update tests:
   - Add/extend tests for domain listing, metadata loading, and missing-artifact behavior
6. Update docs:
   - Add README/demo notes for the new domain
   - Add/extend domain model card and data statement notes

## Training/Export Pattern

For aviation, the scripts already support two local input modes:

- Single labeled CSV (`--input-csv`)
- Split files (`--train-text` + `--train-labels`)

Use the same pattern for future domains with equivalent local scripts.

## Suggested Future Domains

- Maintenance work orders
- Asset failure logs
- Housing repair narratives
- Service disruption tickets
- Safety near-miss reports
- Facilities management requests

## Multi-domain Now, Multimodal-ready Later

Current functionality is text-domain focused: multi-label classification over operational narratives across multiple domains.

Future extensions can layer multimodal inputs on top of this architecture, for example:

- Inspection images
- Asset photos
- PDFs
- Sensor time series
- Maintenance forms
- Audio transcripts

This is future roadmap direction only. The current implementation is text-domain NLP.

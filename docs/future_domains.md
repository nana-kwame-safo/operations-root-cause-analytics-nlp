# Future Domain Expansion

The architecture is intentionally domain-extensible. Aviation incident reports are the first demonstration dataset, while the core software pattern is designed for broader operations intelligence narrative streams.

## Planned Candidate Domains

- Maintenance work orders
- Asset failure logs
- Housing repair narratives
- Service disruption reports
- Operational incident tickets
- Safety near-miss reports
- Facilities management requests

## Architecture Reuse Pattern

Each new domain can reuse the same platform components:
- FastAPI endpoints (`/predict`, `/predict-batch`, `/model-info`)
- threshold-aware prediction and analyst review flags
- explanation cue generation and model metadata reporting
- shared UI workflow with domain selector and model panel

## Domain Onboarding Steps

1. Define domain-specific factor taxonomy and annotation policy.
2. Prepare compliant local dataset and quality checks.
3. Train and evaluate a domain model with compatible output labels.
4. Export artifacts to `artifacts/<domain_id>/`.
5. Add domain config under `app/domains/<domain_id>/`.
6. Validate API/UI behavior and update model/data docs.

## Operational Value

Operations organizations typically handle multiple narrative channels. A shared NLP operations intelligence architecture reduces duplicated engineering effort while preserving domain-specific models, labels, and governance.

## Multi-domain Now, Multimodal-ready Later

Current implementation focus: multi-domain text narrative analytics.

Future expansion direction (not implemented yet): multimodal operational intelligence using inspection images, asset photos, PDFs, sensor time-series streams, maintenance forms, and audio transcripts alongside text narratives.

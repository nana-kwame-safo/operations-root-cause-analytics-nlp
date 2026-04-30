# Architecture Overview

## Goal
Provide a modular NLP operations intelligence prototype where aviation is the first implemented domain, not the full product boundary.

## Components
- `app/api`: HTTP routes and dependency wiring
- `app/services`: domain registry, model loading, prediction, batch scoring, explainability-lite
- `app/schemas`: typed request/response contracts
- `app/domains`: per-domain configuration and label metadata
- `artifacts`: local model artifacts (not committed except examples/placeholders)
- `app/ui`: lightweight analyst-facing interface served by FastAPI

## Request Flow
1. Client calls `/predict` or `/predict-batch`.
2. Domain registry validates implemented domain availability.
3. Model loader resolves artifact and metadata paths by domain.
4. Predictor runs multi-label inference with thresholding and top-k filtering.
5. Explanation service returns transparent cue terms from TF-IDF + linear coefficients.
6. API returns confidence-aware factor indicators with analyst review flags.

## Domain Extensibility Pattern
To add a new domain:
1. Add `app/domains/<domain_id>/domain_config.json`
2. Add label mapping and metadata templates
3. Train/export artifacts under `artifacts/<domain_id>/`
4. Reuse the same prediction pipeline and endpoints

## Diagram Placeholder
Add architecture diagram image here for portfolio presentation:

`docs/images/architecture-diagram.svg`

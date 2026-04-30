# Public Roadmap

This roadmap summarizes planned release increments for **Operations Root Cause Analytics with NLP**.  
Scope and timing may evolve based on contributor bandwidth, data access, and validation outcomes.

## v0.1.0 - ASRS Text-Based MVP

Focus: establish the aviation baseline and analyst-support workflow.

- FastAPI endpoints for health, domains, model info, single prediction, and batch prediction
- Lightweight web UI for single narrative scoring and CSV batch scoring
- TF-IDF + one-vs-rest logistic regression aviation demonstration baseline
- Confidence scores, explanation cues, and review-flag output for analyst triage
- Responsible-use framing for decision-support workflows

## v0.2.0 - Analytics/Dashboard Layer

Focus: improve operational visibility and trend monitoring.

- Aggregated scoring summaries for recurring factor patterns
- Dashboard-ready exports and structured metrics views
- Better filtering/slicing of batch results for analyst teams
- Foundations for threshold tuning and calibration reporting

## v0.3.0 - Multi-Domain Expansion

Focus: extend beyond aviation while preserving domain governance.

- Additional implemented domains through the domain registry pattern
- Domain-specific label mappings, metadata, and validation workflows
- Clear onboarding path for new operations datasets and schemas
- Cross-domain reporting compatibility for downstream analytics

## v0.4.0 - Multimodal-Ready Expansion

Focus: prepare the platform for richer incident evidence types.

- Data contracts for attachments and mixed evidence records
- Support patterns for image/PDF/log references in scoring workflows
- Schema updates for linking text narratives with non-text artifacts
- Responsible-use updates for multimodal evidence handling

## v0.5.0 - Agentic Analyst-Support Workflows

Focus: human-in-the-loop analyst augmentation.

- Guided triage workflows for high-volume incident queues
- Assisted case summarization and follow-up recommendations
- Analyst review orchestration with explicit confidence/risk signals
- Governance controls for role-aware and auditable assistant actions


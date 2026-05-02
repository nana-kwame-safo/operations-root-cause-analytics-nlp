# Explainability Method

## Scope

This project uses a linear multi-label pipeline:

- TF-IDF vectorization
- One-vs-Rest Logistic Regression classifiers

The explainability method is designed for this model family and supports analyst review workflows.

## Contribution Formula

For each predicted label and each active TF-IDF feature in the narrative:

`contribution = TF-IDF value x logistic regression coefficient`

Where:

- `tfidf_value` is the feature weight from the fitted vectorizer
- `class_coefficient` is the coefficient for that feature in the label-specific logistic regression estimator

Only positive contributions are kept as evidence terms. Terms are sorted descending and grouped by importance:

- `high`
- `medium`
- `low`

## Narrative Evidence Highlighting

The service attempts to map top evidence terms back to character spans in the original narrative.

- Case-insensitive exact matching is attempted first
- If a multi-word n-gram is not found as an exact substring, the service attempts a token-level fallback match
- Missing matches are handled gracefully and do not fail prediction responses

## Fallback Behavior

If coefficient extraction is not available (for example, unsupported pipeline structure), the service falls back to token-based cues:

- `explanation_method = "fallback_token_match"`

The app remains usable and still returns analyst-support indicators.

## Why This Method Fits the Current Model

For a linear TF-IDF model, each label-specific classifier learns one coefficient per text feature. Multiplying the active TF-IDF value by the corresponding coefficient gives a local contribution score for that feature in the current narrative.

This is appropriate for the current baseline because coefficient-weighted feature contributions are:

- Fast to compute
- Deterministic
- Easy to audit
- Aligned with sparse text features
- Directly tied to the fitted model used for prediction

This makes the method practical for transparent analyst review support in a lightweight FastAPI app.

## Limitations

- Contribution scores are model-internal signals, not causal evidence
- N-gram span matching can be approximate when phrases are not contiguous
- Label semantics are still draft for some classes and require ongoing review
- Confidence and evidence cues must be interpreted with domain context and human judgment
- Highlighted terms can explain lexical model behavior without proving why the event occurred

## Future Explainability Extensions

- SHAP-based local explanations for richer feature attribution comparisons
- LIME for local perturbation-style interpretation checks
- Similar-case retrieval to show nearest historical narratives with analyst outcomes
- Transformer explanations for future contextual models, including attention/gradient-based approaches where appropriate

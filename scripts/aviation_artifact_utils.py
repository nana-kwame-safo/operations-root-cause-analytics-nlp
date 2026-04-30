"""Shared utilities for aviation artifact training, evaluation, and export."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, hamming_loss
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier

DEFAULT_LABELS = [f"Anomaly_{i}" for i in range(1, 23)]
DEFAULT_THRESHOLD = 0.50

MODEL_NAME = "TF-IDF + One-vs-Rest Logistic Regression"
MODEL_TYPE = "multi-label classification"
TRAINING_APPROACH = "TF-IDF vectorization with One-vs-Rest Logistic Regression"
VERSION = "aviation-demo-v1"

TFIDF_SETTINGS = {
    "ngram_range": (1, 2),
    "max_features": 30000,
    "min_df": 2,
    "strip_accents": "unicode",
    "sublinear_tf": True,
}

LOGISTIC_REGRESSION_SETTINGS = {
    "C": 2.0,
    "max_iter": 400,
    "class_weight": "balanced",
    "solver": "liblinear",
    "random_state": 42,
}

DEFAULT_DATASET_NOTE = (
    "Local frozen NASA ASRS/SIAM 2007 benchmark snapshot used for aviation "
    "demonstration benchmarking."
)
DEFAULT_LIMITATION_NOTE = (
    "Outputs are likely root-cause-related factor indicators for analyst review support "
    "and do not establish definitive causality."
)
DEFAULT_RESPONSIBLE_USE_NOTE = (
    "Decision support only; requires human analyst review and must not be used as a "
    "certified operational safety decision system."
)


def parse_label_columns(raw: str | None) -> list[str] | None:
    if not raw:
        return None
    values = [item.strip() for item in raw.split(",") if item.strip()]
    return values or None


def discover_label_columns(df: pd.DataFrame) -> list[str]:
    found = [c for c in df.columns if c.startswith("Anomaly_")]
    if found:
        return sorted(found, key=lambda x: int(x.split("_")[1]))
    return DEFAULT_LABELS


def _load_text_series(path: Path, text_column: str) -> pd.Series:
    suffix = path.suffix.lower()
    if suffix in {".txt"}:
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines:
            raise ValueError(f"Text file '{path}' is empty.")
        return pd.Series(lines, name=text_column, dtype="string")

    if suffix in {".csv"}:
        df = pd.read_csv(path)
        if text_column in df.columns:
            return df[text_column].fillna("").astype(str)
        if len(df.columns) == 1:
            return df[df.columns[0]].fillna("").astype(str)
        raise ValueError(
            f"Text column '{text_column}' not found in '{path}'. "
            f"Columns available: {list(df.columns)}"
        )

    raise ValueError(
        f"Unsupported text file format for '{path}'. Supported: .txt or .csv"
    )


def load_labeled_dataset(
    *,
    input_csv: Path | None,
    train_text: Path | None,
    train_labels: Path | None,
    text_column: str,
    label_columns: list[str] | None,
) -> tuple[pd.Series, pd.DataFrame, list[str], str]:
    """Load labeled training/evaluation data from single-CSV or split-file format."""
    if input_csv is not None:
        df = pd.read_csv(input_csv)
        if text_column not in df.columns:
            raise ValueError(f"Missing text column '{text_column}' in input CSV.")

        resolved_labels = label_columns or discover_label_columns(df)
        missing = [c for c in resolved_labels if c not in df.columns]
        if missing:
            raise ValueError(f"Missing label columns in input CSV: {missing}")

        texts = df[text_column].fillna("").astype(str)
        labels = df[resolved_labels].fillna(0).astype(int)
        source_note = f"single CSV input ({input_csv})"
        return texts, labels, resolved_labels, source_note

    if train_text is None or train_labels is None:
        raise ValueError(
            "Provide either --input-csv or both --train-text and --train-labels."
        )

    texts = _load_text_series(train_text, text_column).fillna("").astype(str).reset_index(drop=True)
    labels_df = pd.read_csv(train_labels)
    labels_df = labels_df.loc[
        :,
        [c for c in labels_df.columns if not str(c).startswith("Unnamed:")],
    ]
    resolved_labels = label_columns or discover_label_columns(labels_df)

    missing = [c for c in resolved_labels if c not in labels_df.columns]
    if missing:
        raise ValueError(f"Missing label columns in train-labels file: {missing}")

    labels = labels_df[resolved_labels].fillna(0).astype(int).reset_index(drop=True)
    if len(texts) != len(labels):
        raise ValueError(
            "Row count mismatch between train-text and train-labels: "
            f"{len(texts)} text rows vs {len(labels)} label rows."
        )

    source_note = f"split files ({train_text}, {train_labels})"
    return texts, labels, resolved_labels, source_note


def train_bundle(
    *,
    texts: pd.Series,
    labels: pd.DataFrame,
    threshold: float,
    test_size: float,
) -> dict[str, Any]:
    x_train, x_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=test_size,
        random_state=42,
    )

    vectorizer = TfidfVectorizer(**TFIDF_SETTINGS)
    x_train_tfidf = vectorizer.fit_transform(x_train)
    x_test_tfidf = vectorizer.transform(x_test)

    classifier = OneVsRestClassifier(LogisticRegression(**LOGISTIC_REGRESSION_SETTINGS))
    classifier.fit(x_train_tfidf, y_train)

    probas = classifier.predict_proba(x_test_tfidf)
    preds = (np.asarray(probas) >= threshold).astype(int)

    metrics = {
        "micro_f1": float(f1_score(y_test, preds, average="micro", zero_division=0)),
        "macro_f1": float(f1_score(y_test, preds, average="macro", zero_division=0)),
        "samples_f1": float(f1_score(y_test, preds, average="samples", zero_division=0)),
        "hamming_loss": float(hamming_loss(y_test, preds)),
    }

    return {
        "vectorizer": vectorizer,
        "classifier": classifier,
        "metrics": metrics,
        "train_size": int(len(x_train)),
        "test_size": int(len(x_test)),
    }


def build_metadata(
    *,
    labels: list[str],
    threshold: float,
    metrics: dict[str, float],
    source_note: str,
    dataset_provenance_note: str = DEFAULT_DATASET_NOTE,
    limitation_note: str = DEFAULT_LIMITATION_NOTE,
    responsible_use_note: str = DEFAULT_RESPONSIBLE_USE_NOTE,
) -> dict[str, Any]:
    return {
        "domain_id": "aviation",
        "domain": "aviation",
        "model_name": MODEL_NAME,
        "model_type": MODEL_TYPE,
        "training_approach": TRAINING_APPROACH,
        "version": VERSION,
        "training_date": str(date.today()),
        "threshold_default": float(threshold),
        "threshold": float(threshold),
        "label_count": len(labels),
        "labels": labels,
        "tfidf_settings": {
            "ngram_range": list(TFIDF_SETTINGS["ngram_range"]),
            "max_features": TFIDF_SETTINGS["max_features"],
            "min_df": TFIDF_SETTINGS["min_df"],
            "strip_accents": TFIDF_SETTINGS["strip_accents"],
            "sublinear_tf": TFIDF_SETTINGS["sublinear_tf"],
        },
        "logistic_regression_settings": LOGISTIC_REGRESSION_SETTINGS,
        "metrics": metrics,
        "evaluation_metrics": metrics,
        "dataset_provenance_note": dataset_provenance_note,
        "limitation_note": limitation_note,
        "responsible_use_note": responsible_use_note,
        "data_input_format_note": source_note,
    }


def build_label_mapping(labels: list[str]) -> dict[str, dict[str, str]]:
    return {
        label: {
            "display_name": label.replace("_", " "),
            "description": (
                f"Aviation anomaly-factor label '{label}'. "
                "Contributory-factor indicator for analyst review."
            ),
        }
        for label in labels
    }


def write_artifacts(
    *,
    output_dir: Path,
    vectorizer: Any,
    classifier: Any,
    labels: list[str],
    metadata: dict[str, Any],
    label_mapping: dict[str, Any],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "vectorizer": vectorizer,
        "classifier": classifier,
        "labels": labels,
        "metadata": metadata,
    }
    joblib.dump(payload, output_dir / "model.joblib")
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )
    (output_dir / "label_mapping.json").write_text(
        json.dumps(label_mapping, indent=2),
        encoding="utf-8",
    )


def evaluate_artifact(
    *,
    artifact_path: Path,
    texts: pd.Series,
    labels_df: pd.DataFrame,
    threshold: float,
) -> tuple[dict[str, float], list[str]]:
    payload = joblib.load(artifact_path)
    vectorizer = payload.get("vectorizer")
    classifier = payload.get("classifier")
    labels = payload.get("labels", []) or []

    if vectorizer is None or classifier is None or not labels:
        raise ValueError("Artifact must include vectorizer, classifier, and labels.")

    missing = [c for c in labels if c not in labels_df.columns]
    if missing:
        raise ValueError(f"Input data is missing artifact label columns: {missing}")

    x = vectorizer.transform(texts.fillna("").astype(str))
    y_true = labels_df[labels].fillna(0).astype(int).to_numpy()
    y_prob = classifier.predict_proba(x)
    y_pred = (np.asarray(y_prob) >= threshold).astype(int)

    metrics = {
        "micro_f1": float(f1_score(y_true, y_pred, average="micro", zero_division=0)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "samples_f1": float(f1_score(y_true, y_pred, average="samples", zero_division=0)),
        "hamming_loss": float(hamming_loss(y_true, y_pred)),
    }
    return metrics, labels

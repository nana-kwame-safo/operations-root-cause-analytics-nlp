"""Evaluate an aviation artifact on labeled local data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aviation_artifact_utils import DEFAULT_THRESHOLD, evaluate_artifact, load_labeled_dataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)

    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--input-csv",
        type=Path,
        help="Single labeled CSV containing text and Anomaly_* columns.",
    )
    source_group.add_argument(
        "--train-text",
        type=Path,
        help="Text source file (.txt or .csv) for split-file evaluation input.",
    )

    parser.add_argument(
        "--train-labels",
        type=Path,
        help="Label matrix CSV for split-file evaluation input (required with --train-text).",
    )
    parser.add_argument("--text-column", default="text")
    parser.add_argument(
        "--artifact-path",
        type=Path,
        default=Path("artifacts/aviation/model.joblib"),
    )
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    args = parser.parse_args()
    if args.train_text and not args.train_labels:
        parser.error("--train-labels is required when using --train-text.")
    return args


def main() -> None:
    args = parse_args()
    texts, labels_df, _, source_note = load_labeled_dataset(
        input_csv=args.input_csv,
        train_text=args.train_text,
        train_labels=args.train_labels,
        text_column=args.text_column,
        label_columns=None,
    )
    metrics, labels = evaluate_artifact(
        artifact_path=args.artifact_path,
        texts=texts,
        labels_df=labels_df,
        threshold=args.threshold,
    )
    print(f"Evaluated labels: {len(labels)}")
    print(f"Input source: {source_note}")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()

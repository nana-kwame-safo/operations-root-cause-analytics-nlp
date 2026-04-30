"""Train aviation model artifacts from local labeled data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aviation_artifact_utils import (
    DEFAULT_DATASET_NOTE,
    DEFAULT_LIMITATION_NOTE,
    DEFAULT_RESPONSIBLE_USE_NOTE,
    DEFAULT_THRESHOLD,
    build_label_mapping,
    build_metadata,
    load_labeled_dataset,
    parse_label_columns,
    train_bundle,
    write_artifacts,
)


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
        help="Text source file (.txt or .csv) for split-file training input.",
    )

    parser.add_argument(
        "--train-labels",
        type=Path,
        help="Label matrix CSV for split-file training input (required with --train-text).",
    )
    parser.add_argument(
        "--text-column",
        default="text",
        help="Narrative text column name when using CSV text input.",
    )
    parser.add_argument(
        "--label-columns",
        default=None,
        help="Optional comma-separated label columns (defaults to Anomaly_* discovery).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/aviation"),
        help="Artifact output directory.",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Holdout test split used for quick local metrics.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help="Prediction threshold used during local evaluation split.",
    )
    parser.add_argument(
        "--dataset-provenance-note",
        default=DEFAULT_DATASET_NOTE,
        help="Dataset provenance note to persist in metadata.json.",
    )
    parser.add_argument(
        "--limitation-note",
        default=DEFAULT_LIMITATION_NOTE,
        help="Limitation note to persist in metadata.json.",
    )
    parser.add_argument(
        "--responsible-use-note",
        default=DEFAULT_RESPONSIBLE_USE_NOTE,
        help="Responsible-use note to persist in metadata.json.",
    )
    args = parser.parse_args()
    if args.train_text and not args.train_labels:
        parser.error("--train-labels is required when using --train-text.")
    return args


def main() -> None:
    args = parse_args()
    label_columns = parse_label_columns(args.label_columns)

    texts, labels, resolved_labels, source_note = load_labeled_dataset(
        input_csv=args.input_csv,
        train_text=args.train_text,
        train_labels=args.train_labels,
        text_column=args.text_column,
        label_columns=label_columns,
    )
    trained = train_bundle(
        texts=texts,
        labels=labels,
        threshold=args.threshold,
        test_size=args.test_size,
    )
    metadata = build_metadata(
        labels=resolved_labels,
        threshold=args.threshold,
        metrics=trained["metrics"],
        source_note=source_note,
        dataset_provenance_note=args.dataset_provenance_note,
        limitation_note=args.limitation_note,
        responsible_use_note=args.responsible_use_note,
    )
    label_mapping = build_label_mapping(resolved_labels)

    write_artifacts(
        output_dir=args.output_dir,
        vectorizer=trained["vectorizer"],
        classifier=trained["classifier"],
        labels=resolved_labels,
        metadata=metadata,
        label_mapping=label_mapping,
    )

    print("Training complete.")
    print(f"Input source: {source_note}")
    print(
        f"Split sizes -> train: {trained['train_size']} rows, test: {trained['test_size']} rows"
    )
    print(json.dumps(trained["metrics"], indent=2))
    print(f"Artifacts written to: {args.output_dir}")


if __name__ == "__main__":
    main()

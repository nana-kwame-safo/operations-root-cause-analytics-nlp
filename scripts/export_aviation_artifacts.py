"""Export aviation artifacts by copy or train-and-export workflow."""

from __future__ import annotations

import argparse
import shutil
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

EXPECTED_FILES = ["model.joblib", "metadata.json", "label_mapping.json"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=None,
        help="Directory containing generated artifact files to copy directly.",
    )
    parser.add_argument(
        "--input-csv",
        type=Path,
        default=None,
        help="Single labeled CSV containing text and Anomaly_* columns.",
    )
    parser.add_argument(
        "--train-text",
        type=Path,
        default=None,
        help="Text source file (.txt or .csv) for split-file training input.",
    )
    parser.add_argument(
        "--train-labels",
        type=Path,
        default=None,
        help="Label matrix CSV for split-file training input.",
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
    parser.add_argument(
        "--output-dir",
        "--target-dir",
        dest="output_dir",
        type=Path,
        default=Path("artifacts/aviation"),
        help="Repository artifact destination directory.",
    )
    args = parser.parse_args()

    if args.source_dir is None and args.input_csv is None and args.train_text is None:
        parser.error(
            "Provide one mode: --source-dir, --input-csv, or --train-text with --train-labels."
        )

    if args.train_text and not args.train_labels:
        parser.error("--train-labels is required when using --train-text.")

    if args.source_dir and (args.input_csv or args.train_text or args.train_labels):
        parser.error(
            "Use either copy mode (--source-dir) or train-and-export mode "
            "(--input-csv or --train-text/--train-labels), not both."
        )

    return args


def copy_export(*, source_dir: Path, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []

    for filename in EXPECTED_FILES:
        src = source_dir / filename
        if not src.exists():
            print(f"Skipping missing file: {src}")
            continue
        dst = output_dir / filename
        shutil.copy2(src, dst)
        copied.append(dst)

    if not copied:
        raise FileNotFoundError("No expected artifact files were found in source-dir.")
    return copied


def train_and_export(args: argparse.Namespace) -> None:
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
    print("Training + export complete.")
    print(f"Input source: {source_note}")
    print(f"Artifacts written to: {args.output_dir}")


def main() -> None:
    args = parse_args()
    if args.source_dir:
        copied = copy_export(source_dir=args.source_dir, output_dir=args.output_dir)
        print("Exported files:")
        for path in copied:
            print(f"- {path}")
        return

    train_and_export(args)


if __name__ == "__main__":
    main()

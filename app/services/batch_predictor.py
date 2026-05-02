"""Batch prediction service."""

from __future__ import annotations

from dataclasses import dataclass

from app.services.predictor import Predictor


@dataclass
class BatchPredictor:
    predictor: Predictor

    def predict_rows(
        self,
        rows: list[str],
        domain: str,
        threshold: float,
        top_k: int,
    ) -> list[dict]:
        results: list[dict] = []
        for idx, text in enumerate(rows):
            text_value = (text or "").strip()
            if not text_value:
                results.append(
                    {
                        "row_index": idx,
                        "input_text": text,
                        "predicted_labels": [],
                        "review_flag": True,
                        "message": "Empty narrative text — analyst review recommended.",
                    }
                )
                continue

            prediction = self.predictor.predict(
                text=text_value,
                domain=domain,
                threshold=threshold,
                top_k=top_k,
            )
            results.append(
                {
                    "row_index": idx,
                    "input_text": text_value,
                    "predicted_labels": prediction["predicted_labels"],
                    "predicted_label_ids": [
                        item.get("label_id", item.get("label", ""))
                        for item in prediction["predicted_labels"]
                    ],
                    "predicted_label_names": [
                        item.get("label_name", item.get("label", ""))
                        for item in prediction["predicted_labels"]
                    ],
                    "review_flag": prediction["review_flag"],
                    "message": prediction["message"],
                }
            )
        return results

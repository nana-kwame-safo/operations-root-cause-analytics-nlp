from __future__ import annotations

import asyncio

import pytest
from fastapi import HTTPException

from app.api.routes import predict_batch


class FakeUploadFile:
    def __init__(self, content: str) -> None:
        self._content = content.encode("utf-8")

    async def read(self) -> bytes:
        return self._content


class FakeBatchPredictor:
    def predict_rows(self, rows, domain: str, threshold: float, top_k: int):
        results = []
        for idx, text in enumerate(rows):
            results.append(
                {
                    "row_index": idx,
                    "input_text": text,
                    "predicted_labels": [
                        {
                            "label": "Anomaly_1",
                            "label_id": "Anomaly_1",
                            "label_name": "Draft Communication and Coordination Indicator",
                            "short_name": "Comm Coordination",
                            "score": 0.77,
                            "score_percent": 77.0,
                            "plain_language_description": "Demo description.",
                            "technical_description": "Demo technical description.",
                            "operational_interpretation": "Demo operational interpretation.",
                            "review_guidance": "Demo review guidance.",
                            "taxonomy_status": "draft_from_model_features",
                            "confidence_note": "Demo confidence note.",
                            "example_cues": ["approach"],
                            "evidence_terms": [],
                            "evidence_spans": [],
                            "explanation_terms": ["approach", "altitude", "instruction"],
                            "explanation_method": "fallback_token_match",
                        }
                    ],
                    "predicted_label_ids": ["Anomaly_1"],
                    "predicted_label_names": [
                        "Draft Communication and Coordination Indicator",
                    ],
                    "review_flag": False,
                    "message": "Predictions generated successfully.",
                }
            )
        return results


def test_batch_upload_happy_path():
    content = "text\ncrew reported late clearance\ncontroller instruction mismatch\n"
    upload = FakeUploadFile(content)

    response = asyncio.run(
        predict_batch(
            file=upload,
            domain="aviation",
            threshold=0.5,
            top_k=5,
            text_column="text",
            batch_predictor=FakeBatchPredictor(),
        )
    )
    payload = response.model_dump()
    assert payload["row_count"] == 2
    assert len(payload["results"]) == 2
    assert payload["results"][0]["predicted_labels"][0]["label"] == "Anomaly_1"
    assert payload["results"][0]["predicted_label_names"][0]


def test_batch_upload_missing_text_column_returns_422():
    content = "narrative\nrow one\nrow two\n"
    upload = FakeUploadFile(content)

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            predict_batch(
                file=upload,
                domain="aviation",
                threshold=0.5,
                top_k=5,
                text_column="text",
                batch_predictor=FakeBatchPredictor(),
            )
        )
    assert exc.value.status_code == 422

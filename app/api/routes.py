"""API routes."""

from __future__ import annotations

import csv
import io
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.api.dependencies import (
    get_batch_predictor,
    get_domain_registry,
    get_model_loader,
    get_predictor,
    settings_dependency,
)
from app.core.constants import APP_FULL_NAME, LIMITATION_NOTE
from app.core.config import Settings
from app.schemas.batch import BatchPredictionResponse
from app.schemas.model_info import EvaluationMetrics, ModelInfoResponse
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.batch_predictor import BatchPredictor
from app.services.domain_registry import DomainRegistry
from app.services.model_loader import ModelLoader
from app.services.predictor import (
    DomainNotImplementedError,
    ModelUnavailableError,
    Predictor,
)

router = APIRouter()


@router.get("/health")
def health(settings: Settings = Depends(settings_dependency)) -> dict[str, str]:
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "active_domain": settings.active_domain,
        "version": settings.app_version,
    }


@router.get("/domains")
def domains(registry: DomainRegistry = Depends(get_domain_registry)) -> dict[str, list[dict[str, str]]]:
    return {"available_domains": registry.list_domains()}


@router.get("/model-info", response_model=ModelInfoResponse)
def model_info(
    domain: str | None = None,
    settings: Settings = Depends(settings_dependency),
    registry: DomainRegistry = Depends(get_domain_registry),
    loader: ModelLoader = Depends(get_model_loader),
) -> ModelInfoResponse:
    selected_domain = domain or settings.active_domain
    if not registry.is_implemented(selected_domain):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain '{selected_domain}' is not implemented.",
        )

    config = registry.get_config(selected_domain).raw
    bundle = loader.get_bundle(selected_domain)
    metadata = bundle.metadata
    metrics = metadata.get("evaluation_metrics", {})

    return ModelInfoResponse(
        app_name=APP_FULL_NAME,
        active_domain=selected_domain,
        model_name=metadata.get("model_name", config.get("model_name", "Unknown model")),
        model_type=metadata.get("model_type", config.get("model_type", "Unknown type")),
        label_count=int(metadata.get("label_count", config.get("label_count", len(bundle.labels)))),
        threshold=float(
            metadata.get(
                "threshold_default",
                config.get("default_threshold", settings.default_threshold),
            )
        ),
        training_approach=metadata.get(
            "training_approach",
            "TF-IDF vectorization with One-vs-Rest Logistic Regression",
        ),
        version=metadata.get("version", "aviation-demo-v1"),
        training_date=metadata.get("training_date", "YYYY-MM-DD"),
        dataset_provenance_note=metadata.get(
            "dataset_provenance_note",
            config.get("dataset_provenance_note", ""),
        ),
        evaluation_metrics=EvaluationMetrics(
            micro_f1=metrics.get("micro_f1"),
            macro_f1=metrics.get("macro_f1"),
            samples_f1=metrics.get("samples_f1"),
            hamming_loss=metrics.get("hamming_loss"),
        ),
        limitation_note=metadata.get(
            "limitation_note",
            config.get("limitation_note", LIMITATION_NOTE),
        ),
        artifact_status=bundle.artifact_status,
    )


@router.post("/predict", response_model=PredictionResponse)
def predict(
    request: PredictionRequest,
    predictor: Predictor = Depends(get_predictor),
) -> PredictionResponse:
    try:
        result = predictor.predict(
            text=request.text,
            domain=request.domain,
            threshold=request.threshold,
            top_k=request.top_k,
        )
    except DomainNotImplementedError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ModelUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return PredictionResponse(**result)


@router.post("/predict-batch", response_model=BatchPredictionResponse)
async def predict_batch(
    file: Annotated[UploadFile, File(description="CSV file containing incident narratives.")],
    domain: Annotated[str, Form()] = "aviation",
    threshold: Annotated[float, Form(ge=0.0, le=1.0)] = 0.5,
    top_k: Annotated[int, Form(ge=1, le=22)] = 5,
    text_column: Annotated[str, Form()] = "text",
    batch_predictor: BatchPredictor = Depends(get_batch_predictor),
) -> BatchPredictionResponse:
    try:
        payload = await file.read()
        decoded = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file must be UTF-8 encoded.",
        ) from exc

    reader = csv.DictReader(io.StringIO(decoded))
    if reader.fieldnames is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file appears empty or malformed.",
        )
    if text_column not in reader.fieldnames:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"CSV must contain text column '{text_column}'. "
                f"Available columns: {reader.fieldnames}"
            ),
        )

    rows = [(row.get(text_column) or "").strip() for row in reader]
    try:
        results = batch_predictor.predict_rows(
            rows=rows,
            domain=domain,
            threshold=threshold,
            top_k=top_k,
        )
    except DomainNotImplementedError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ModelUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return BatchPredictionResponse(
        domain=domain,
        threshold_used=threshold,
        top_k_used=top_k,
        text_column=text_column,
        row_count=len(results),
        results=results,
    )

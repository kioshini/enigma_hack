"""
ML analysis endpoint.

Exposed as an internal REST API so it can later be extracted
into a separate microservice container.
"""

from fastapi import APIRouter
from app.schemas import MLAnalysisRequest, MLAnalysisResponse
from app.services.ml_service import analyze_email

router = APIRouter(prefix="/api/v1/ml", tags=["ml"])


@router.post("/analyze", response_model=MLAnalysisResponse)
def analyze(request: MLAnalysisRequest):
    """
    Analyze email text and return classification.

    This endpoint exists so the ML service can later be extracted
    to a dedicated container without changing the pipeline code.
    """
    result = analyze_email(request.text)
    return result

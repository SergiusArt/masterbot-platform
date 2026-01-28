"""Reports API endpoints."""

from fastapi import APIRouter, HTTPException

from services.report_service import report_service
from shared.schemas.impulse import ReportRequest, ReportResponse

router = APIRouter()


@router.post("/generate", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """Generate report for user.

    Args:
        request: Report generation request

    Returns:
        Generated report
    """
    try:
        report = await report_service.generate_report(
            report_type=request.type,
            user_id=request.user_id,
        )
        return ReportResponse(status="success", report=report)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

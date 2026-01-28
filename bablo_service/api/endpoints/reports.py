"""Reports API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session
from services.report_service import report_service

router = APIRouter(prefix="/reports", tags=["reports"])

VALID_REPORT_TYPES = ["morning", "evening", "weekly", "monthly"]


@router.post("/generate")
async def generate_report(
    report_type: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Generate report on demand."""
    if report_type not in VALID_REPORT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid report type. Must be one of: {VALID_REPORT_TYPES}",
        )

    report = await report_service.generate_report(session, report_type)
    return {"status": "ok", "report": report}


@router.get("/data/{report_type}")
async def get_report_data(
    report_type: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Get raw report data for aggregation."""
    if report_type not in VALID_REPORT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid report type. Must be one of: {VALID_REPORT_TYPES}",
        )

    data = await report_service.get_report_data(session, report_type)
    return data

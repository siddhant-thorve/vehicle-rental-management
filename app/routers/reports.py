from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.report import UtilisationReportResponse, RevenueReportResponse
from app.services.report_service import ReportService
from app.core.security import require_role

router = APIRouter(prefix="/reports", tags=["Reporting & Analytics"])


@router.get("/utilisation", response_model=UtilisationReportResponse)
def get_fleet_utilisation(
    from_date: date = Query(..., alias="from", description="Start date (YYYY-MM-DD)"),
    to_date: date = Query(..., alias="to", description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    _admin=Depends(require_role("ADMIN")),
):
    return ReportService.get_utilisation_report(db, from_date=from_date, to_date=to_date)


@router.get("/revenue", response_model=RevenueReportResponse)
def get_revenue_report(
    from_date: date = Query(..., alias="from", description="Start date (YYYY-MM-DD)"),
    to_date: date = Query(..., alias="to", description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    _admin=Depends(require_role("ADMIN")),
):
    return ReportService.get_revenue_report(db, from_date=from_date, to_date=to_date)

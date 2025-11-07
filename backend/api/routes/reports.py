"""
Reports routes
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import structlog

logger = structlog.get_logger()

router = APIRouter()


class Report(BaseModel):
    id: str
    name: str
    type: str
    generated_date: str
    status: str


@router.get("/{project_id}", response_model=List[Report])
async def list_reports(project_id: str):
    """List reports for a project"""
    return [
        {
            "id": "report-1",
            "name": "Executive Summary",
            "type": "executive_summary",
            "generated_date": "2024-11-07T10:00:00Z",
            "status": "completed",
        },
        {
            "id": "report-2",
            "name": "Technical Analysis",
            "type": "technical",
            "generated_date": "2024-11-06T15:30:00Z",
            "status": "completed",
        },
    ]


@router.post("/{project_id}/generate")
async def generate_report(project_id: str, report_type: str):
    """Generate a new report"""
    logger.info("Generating report", project_id=project_id, report_type=report_type)

    return {
        "id": "report-new",
        "name": f"{report_type.replace('_', ' ').title()}",
        "type": report_type,
        "generated_date": "2024-11-07T11:00:00Z",
        "status": "generating",
        "message": "Report generation started",
    }


@router.get("/{project_id}/{report_id}/download")
async def download_report(project_id: str, report_id: str):
    """Download a report"""
    logger.info("Downloading report", project_id=project_id, report_id=report_id)

    return {
        "url": f"/api/v1/reports/{project_id}/{report_id}/file",
        "expires_at": "2024-11-07T12:00:00Z",
    }

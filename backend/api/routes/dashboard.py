"""
Dashboard routes
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict
import structlog

logger = structlog.get_logger()

router = APIRouter()


class DDProgress(BaseModel):
    total_items: int
    completed_items: int
    completion_percentage: float
    by_category: Dict[str, Dict[str, int]]


@router.get("/dd-progress/{project_id}", response_model=DDProgress)
async def get_dd_progress(project_id: str):
    """Get DD progress for a project based on uploaded documents"""
    logger.info("Fetching DD progress", project_id=project_id)

    # Import uploaded documents
    from api.routes.documents import uploaded_documents

    # Get documents for this project
    project_docs = uploaded_documents.get(project_id, [])

    # Count documents by category
    category_counts = {}
    for doc in project_docs:
        category = doc.get('category', 'Uncategorized')
        if category not in category_counts:
            category_counts[category] = 0
        category_counts[category] += 1

    # Build by_category structure
    # For now, all uploaded docs are considered "completed"
    by_category = {}
    for category, count in category_counts.items():
        by_category[category] = {
            "total": count,
            "completed": count  # All uploaded docs are considered complete
        }

    # Calculate totals
    total_items = len(project_docs)
    completed_items = len(project_docs)  # All uploaded docs are complete
    completion_percentage = 100.0 if total_items > 0 else 0.0

    return {
        "total_items": total_items,
        "completed_items": completed_items,
        "completion_percentage": completion_percentage,
        "by_category": by_category,
    }


@router.get("/stats/{project_id}")
async def get_project_stats(project_id: str):
    """Get project statistics based on real data"""
    from api.routes.documents import uploaded_documents

    # Get real document count
    project_docs = uploaded_documents.get(project_id, [])
    doc_count = len(project_docs)

    return {
        "documents_processed": doc_count,
        "questions_answered": 0,  # TODO: Track Q&A history
        "days_until_closing": 14,  # TODO: Get from project settings
        "total_issues": 0,  # TODO: Track issues
        "critical_issues": 0,  # TODO: Track critical issues
    }

"""
Projects routes
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import structlog

logger = structlog.get_logger()

router = APIRouter()


class Project(BaseModel):
    id: str
    name: str
    technology: str
    capacity_mw: float
    location: str
    status: str


@router.get("", response_model=List[Project])
async def list_projects():
    """List all projects"""
    return [
        {
            "id": "demo-project",
            "name": "Demo Solar Project",
            "technology": "Solar",
            "capacity_mw": 50.0,
            "location": "California",
            "status": "active",
        }
    ]


@router.post("", response_model=Project)
async def create_project(project: Project):
    """Create a new project"""
    logger.info("Creating project", name=project.name)
    return project


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """Get project by ID"""
    return {
        "id": project_id,
        "name": "Demo Solar Project",
        "technology": "Solar",
        "capacity_mw": 50.0,
        "location": "California",
        "status": "active",
    }


@router.put("/{project_id}", response_model=Project)
async def update_project(project_id: str, project: Project):
    """Update a project"""
    logger.info("Updating project", project_id=project_id)
    project.id = project_id
    return project


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    logger.info("Deleting project", project_id=project_id)
    return {"message": "Project deleted successfully"}

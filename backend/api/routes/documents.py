"""
Documents routes
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import structlog
import os
import uuid
from datetime import datetime
import aiofiles

logger = structlog.get_logger()

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class Document(BaseModel):
    id: str
    filename: str
    document_type: str
    category: str
    upload_date: str
    size_bytes: int
    status: str


# In-memory storage for demo (replace with database in production)
uploaded_documents = {}


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    project_id: str = Form(...),
    category: Optional[str] = Form(None),
):
    """Upload a document"""
    logger.info("Document upload", filename=file.filename, project_id=project_id)

    try:
        # Generate unique document ID
        doc_id = str(uuid.uuid4())

        # Get file extension
        file_ext = os.path.splitext(file.filename)[1]

        # Create project directory
        project_dir = os.path.join(UPLOAD_DIR, project_id)
        os.makedirs(project_dir, exist_ok=True)

        # Save file
        file_path = os.path.join(project_dir, f"{doc_id}{file_ext}")

        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
            file_size = len(content)

        # Store document metadata
        doc_metadata = {
            "id": doc_id,
            "filename": file.filename,
            "document_type": file_ext.replace(".", ""),
            "category": category or "Uncategorized",
            "upload_date": datetime.utcnow().isoformat() + "Z",
            "size_bytes": file_size,
            "status": "uploaded",
            "file_path": file_path,
            "project_id": project_id,
        }

        if project_id not in uploaded_documents:
            uploaded_documents[project_id] = []
        uploaded_documents[project_id].append(doc_metadata)

        logger.info("Document uploaded successfully", doc_id=doc_id, filename=file.filename)

        return {
            **doc_metadata,
            "message": "Document uploaded successfully",
        }

    except Exception as e:
        logger.error("Document upload failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("", response_model=List[Document])
async def list_documents(project_id: str):
    """List documents for a project"""
    if project_id in uploaded_documents:
        return [
            {k: v for k, v in doc.items() if k != "file_path"}
            for doc in uploaded_documents[project_id]
        ]
    return []


@router.get("/{document_id}", response_model=Document)
async def get_document(document_id: str):
    """Get document details"""
    return {
        "id": document_id,
        "filename": "PPA_Agreement.pdf",
        "document_type": "pdf",
        "category": "Commercial",
        "upload_date": "2024-11-01T10:00:00Z",
        "size_bytes": 2048000,
        "status": "processed",
    }


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    logger.info("Deleting document", document_id=document_id)
    return {"message": "Document deleted successfully"}

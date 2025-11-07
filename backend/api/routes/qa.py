"""
Q&A routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import structlog
from openai import AsyncOpenAI
from api.config import settings
import os

logger = structlog.get_logger()

router = APIRouter()

# Initialize OpenAI client
openai_client = None
if settings.OPENAI_API_KEY:
    openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class Source(BaseModel):
    document_id: str
    filename: str
    document_type: str
    relevance_score: float


class QuestionRequest(BaseModel):
    project_id: str
    question: str


class AnswerResponse(BaseModel):
    answer: str
    sources: List[Source]
    confidence: float


async def read_document_content(file_path: str, max_chars: int = 10000) -> str:
    """Read document content - supports PDF, TXT, and other text formats"""
    try:
        if not os.path.exists(file_path):
            return ""

        file_ext = os.path.splitext(file_path)[1].lower()

        # Handle PDF files
        if file_ext == '.pdf':
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    text_parts = []
                    # Read first 10 pages max
                    for page_num in range(min(10, len(pdf_reader.pages))):
                        page = pdf_reader.pages[page_num]
                        text_parts.append(page.extract_text())
                    content = "\n".join(text_parts)
                    return content[:max_chars]
            except Exception as pdf_error:
                logger.warning(f"PDF extraction failed, trying pdfplumber: {str(pdf_error)}")
                try:
                    import pdfplumber
                    with pdfplumber.open(file_path) as pdf:
                        text_parts = []
                        for page in pdf.pages[:10]:  # First 10 pages
                            text_parts.append(page.extract_text() or "")
                        content = "\n".join(text_parts)
                        return content[:max_chars]
                except Exception as e2:
                    logger.warning(f"pdfplumber also failed: {str(e2)}")
                    return ""

        # Handle text files
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(max_chars)
            return content

    except Exception as e:
        logger.warning(f"Could not read document: {str(e)}")
        return ""


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question about project documents"""
    logger.info("Question asked", question=request.question, project_id=request.project_id)

    if not openai_client:
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key not configured. Please set OPENAI_API_KEY in environment."
        )

    try:
        # Import uploaded documents from documents route
        from api.routes.documents import uploaded_documents

        # Get documents for this project
        project_docs = uploaded_documents.get(request.project_id, [])

        if not project_docs:
            return {
                "answer": "No documents have been uploaded yet for this project. Please upload some documents first to ask questions about them.",
                "sources": [],
                "confidence": 0.0,
            }

        # Read content from uploaded documents
        context_parts = []
        sources = []

        for doc in project_docs[:5]:  # Limit to first 5 docs
            content = await read_document_content(doc.get('file_path', ''))
            if content:
                context_parts.append(f"Document: {doc['filename']}\n{content[:2000]}")
                sources.append({
                    "document_id": doc['id'],
                    "filename": doc['filename'],
                    "document_type": doc['document_type'],
                    "relevance_score": 0.85,
                })

        if not context_parts:
            context = "No readable document content available yet."
        else:
            context = "\n\n".join(context_parts)

        # Create prompt for OpenAI
        system_prompt = """You are an expert assistant for renewable energy due diligence.
        Analyze the provided documents and answer questions accurately.
        If you cannot find the answer in the documents, say so clearly.
        Provide specific references to the documents when possible."""

        user_prompt = f"""Based on the following documents:

{context}

Question: {request.question}

Please provide a detailed answer based on the document content."""

        # Call OpenAI API
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Using mini for cost efficiency
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=1000,
        )

        answer = response.choices[0].message.content

        return {
            "answer": answer,
            "sources": sources,
            "confidence": 0.85,
        }

    except Exception as e:
        logger.error("Q&A failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Q&A processing failed: {str(e)}")


@router.get("/history/{project_id}")
async def get_qa_history(project_id: str):
    """Get Q&A history for a project"""
    return {
        "questions": [
            {
                "id": "q1",
                "question": "What is the PPA price?",
                "answer": "$45/MWh with 2% annual escalation",
                "timestamp": "2024-11-07T09:30:00Z",
            },
            {
                "id": "q2",
                "question": "What are the key risks?",
                "answer": "Main risks include interconnection delays and equipment supply chain issues",
                "timestamp": "2024-11-07T10:15:00Z",
            },
        ]
    }

# API Documentation - Renewable DD Tool

Base URL: `https://api.your-domain.com/api/v1`

## Authentication

All API requests require authentication using JWT Bearer tokens obtained through Google OAuth 2.0.

### Headers
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

## Authentication Endpoints

### GET /auth/google/login
Initiate Google OAuth login flow.

**Response:**
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/auth?..."
}
```

### POST /auth/google/callback
Handle OAuth callback and issue JWT token.

**Request Body:**
```json
{
  "code": "4/0AY0e-g7..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "user_id": "123",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "reviewer"
  }
}
```

## Project Management

### GET /projects
List all DD projects for authenticated user.

**Query Parameters:**
- `status` (optional): Filter by status (active, completed, archived)
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)

**Response:**
```json
{
  "projects": [
    {
      "project_id": "proj_123",
      "name": "Solar Farm Alpha - 50MW",
      "technology_type": "solar",
      "capacity_mw": 50.0,
      "location": "California, USA",
      "status": "active",
      "completion_percentage": 67.5,
      "created_at": "2024-01-15T10:30:00Z",
      "drive_folder_id": "1abc..."
    }
  ],
  "total": 15,
  "page": 1,
  "per_page": 20
}
```

### POST /projects
Create a new DD project.

**Request Body:**
```json
{
  "name": "Wind Farm Beta - 100MW",
  "technology_type": "wind",
  "capacity_mw": 100.0,
  "location": "Texas, USA",
  "expected_cod": "2025-12-31",
  "description": "100MW wind project in West Texas"
}
```

**Response:**
```json
{
  "project_id": "proj_124",
  "name": "Wind Farm Beta - 100MW",
  "drive_folders": {
    "root": "folder_id_root",
    "Legal": "folder_id_legal",
    "Technical": "folder_id_technical",
    "Financial": "folder_id_financial",
    "Environmental": "folder_id_environmental",
    "Commercial": "folder_id_commercial"
  },
  "created_at": "2024-01-20T15:45:00Z"
}
```

### GET /projects/{project_id}
Get detailed project information.

**Response:**
```json
{
  "project_id": "proj_123",
  "name": "Solar Farm Alpha - 50MW",
  "technology_type": "solar",
  "capacity_mw": 50.0,
  "location": "California, USA",
  "expected_cod": "2025-06-30",
  "status": "active",
  "completion_status": {
    "overall": 67.5,
    "by_category": {
      "Legal": 80.0,
      "Technical": 65.0,
      "Financial": 50.0,
      "Environmental": 75.0,
      "Commercial": 70.0
    }
  },
  "key_metrics": {
    "total_documents": 45,
    "reviewed_documents": 38,
    "critical_issues": 2,
    "high_issues": 5
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T09:15:00Z"
}
```

## Document Management

### POST /documents/upload
Upload document to project data room.

**Request:**
- Content-Type: multipart/form-data
- Body:
  - `file`: Document file (PDF, DOCX, XLSX, etc.)
  - `project_id`: Project ID
  - `category`: Document category (Legal, Technical, Financial, Environmental, Commercial)
  - `description` (optional): Document description

**Response:**
```json
{
  "document_id": "doc_456",
  "filename": "PPA_Agreement.pdf",
  "file_size": 2457600,
  "category": "Commercial",
  "drive_file_id": "1xyz...",
  "classification": {
    "document_type": "ppa",
    "confidence": 0.95,
    "classification_method": "llm"
  },
  "upload_status": "processing",
  "uploaded_at": "2024-01-20T16:30:00Z"
}
```

### GET /documents/{document_id}
Get document details and metadata.

**Response:**
```json
{
  "document_id": "doc_456",
  "filename": "PPA_Agreement.pdf",
  "document_type": "ppa",
  "category": "Commercial",
  "file_size": 2457600,
  "page_count": 85,
  "status": "processed",
  "classification": {
    "document_type": "ppa",
    "confidence": 0.95
  },
  "extracted_terms": {
    "seller": "Solar Energy LLC",
    "buyer": "Utility Corp",
    "energy_price": "$45.50/MWh",
    "delivery_term_years": 20,
    "contract_capacity_mw": 50.0,
    "red_flags": [
      "Short contract term compared to industry standard"
    ]
  },
  "indexed_for_qa": true,
  "uploaded_at": "2024-01-20T16:30:00Z",
  "processed_at": "2024-01-20T16:32:15Z"
}
```

### GET /documents
List documents in project.

**Query Parameters:**
- `project_id`: Project ID (required)
- `category`: Filter by category
- `document_type`: Filter by document type
- `status`: Filter by status (uploaded, processing, processed, failed)

**Response:**
```json
{
  "documents": [
    {
      "document_id": "doc_456",
      "filename": "PPA_Agreement.pdf",
      "document_type": "ppa",
      "category": "Commercial",
      "status": "processed",
      "uploaded_at": "2024-01-20T16:30:00Z"
    }
  ],
  "total": 45
}
```

### DELETE /documents/{document_id}
Delete document from data room.

**Response:**
```json
{
  "message": "Document deleted successfully",
  "document_id": "doc_456"
}
```

## Dashboard and Progress

### GET /dashboard/{project_id}
Get dashboard data for project.

**Response:**
```json
{
  "project_info": {
    "project_id": "proj_123",
    "name": "Solar Farm Alpha - 50MW",
    "capacity_mw": 50.0
  },
  "completion_status": {
    "total_items": 85,
    "completed_items": 57,
    "completion_percentage": 67.1,
    "by_category": {
      "Legal": {"total": 20, "completed": 16},
      "Technical": {"total": 25, "completed": 18},
      "Financial": {"total": 15, "completed": 8},
      "Environmental": {"total": 15, "completed": 10},
      "Commercial": {"total": 10, "completed": 5}
    }
  },
  "checklist": [...],
  "recent_activity": [...],
  "issues": [
    {
      "issue_id": "issue_789",
      "severity": "Critical",
      "description": "Missing interconnection agreement",
      "category": "Technical",
      "status": "open",
      "created_at": "2024-01-18T10:00:00Z"
    }
  ]
}
```

### GET /dashboard/{project_id}/checklist
Get DD checklist with status.

**Response:**
```json
{
  "checklist_items": [
    {
      "id": "legal_001",
      "category": "Legal",
      "subcategory": "Corporate Structure",
      "item_name": "Articles of Incorporation/Formation",
      "description": "Certified copies of articles of incorporation or formation",
      "priority": "critical",
      "responsible_party": "seller",
      "status": "approved",
      "document_ids": ["doc_101"],
      "notes": "Received and reviewed",
      "reviewer_comments": "All documents in order"
    }
  ],
  "completion_stats": {
    "total_items": 85,
    "completed_items": 57,
    "completion_percentage": 67.1
  }
}
```

### PUT /dashboard/{project_id}/checklist/{item_id}
Update checklist item status.

**Request Body:**
```json
{
  "status": "approved",
  "notes": "Document reviewed and approved",
  "reviewer_comments": "All terms acceptable",
  "document_ids": ["doc_101", "doc_102"]
}
```

**Response:**
```json
{
  "message": "Checklist item updated",
  "item_id": "legal_001",
  "status": "approved"
}
```

## Q&A System

### POST /qa/ask
Ask a question about project documents.

**Request Body:**
```json
{
  "project_id": "proj_123",
  "question": "What is the PPA price and escalation rate?",
  "document_types": ["ppa", "offtake_agreement"],
  "max_sources": 5
}
```

**Response:**
```json
{
  "answer": "According to the Power Purchase Agreement dated January 15, 2024, the energy price is $45.50 per MWh with an annual escalation rate of 2.5% beginning in Year 3. This pricing structure is competitive for utility-scale solar projects in California.\n\nKey terms:\n- Base price: $45.50/MWh\n- Escalation: 2.5% annually starting Year 3\n- No escalation in Years 1-2\n- Price applies to all energy delivered",
  "sources": [
    {
      "document_id": "doc_456",
      "filename": "PPA_Agreement.pdf",
      "document_type": "ppa",
      "relevance_score": 0.92
    }
  ],
  "confidence": 0.89,
  "question": "What is the PPA price and escalation rate?"
}
```

### POST /qa/compare
Compare terms across multiple documents.

**Request Body:**
```json
{
  "project_id": "proj_123",
  "question": "Compare warranty terms",
  "document_ids": ["doc_301", "doc_302", "doc_303"]
}
```

**Response:**
```json
{
  "answer": "Comparison of warranty terms across three equipment contracts:\n\n**Solar Panel Warranty (Doc 301):**\n- Product warranty: 12 years\n- Performance warranty: 25 years (90% at Year 10, 80% at Year 25)\n\n**Inverter Warranty (Doc 302):**\n- Product warranty: 10 years\n- Extended warranty available: Up to 20 years\n\n**Tracking System Warranty (Doc 303):**\n- Product warranty: 5 years\n- Performance guarantee: 99% availability\n\n**Key Findings:**\n- Panel warranties are industry-standard\n- Inverter warranty is shorter than typical (15 years)\n- Tracking warranty is adequate but consider extended coverage",
  "sources": [...],
  "comparison_type": "multi_document"
}
```

## Reports and Summaries

### GET /reports/{project_id}/executive-summary
Generate executive summary of DD status.

**Response:**
```json
{
  "generated_at": "2024-01-20T18:00:00Z",
  "narrative": "# Executive Summary: Solar Farm Alpha - 50MW\n\n## Project Overview\n...",
  "metrics": {
    "completion_percentage": 67.5,
    "documents_reviewed": 38,
    "total_documents_required": 85,
    "critical_issues": 2,
    "high_issues": 5,
    "medium_issues": 12,
    "estimated_lifetime_revenue_usd": 89500000,
    "estimated_annual_revenue_usd": 4475000
  },
  "deal_breakers": [],
  "action_items": [
    {
      "priority": "Critical",
      "action": "Resolve: Missing interconnection agreement",
      "owner": "Seller",
      "deadline": "Immediate"
    }
  ],
  "overall_risk_rating": "MEDIUM",
  "recommendation": "CONTINUE DD - Complete outstanding items and address identified issues"
}
```

### POST /reports/{project_id}/export
Export DD report in various formats.

**Request Body:**
```json
{
  "format": "pdf",
  "sections": ["summary", "checklist", "findings", "documents"],
  "include_confidential": false
}
```

**Response:**
- Content-Type: application/pdf or application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
- Binary file download

## User Management (Admin Only)

### GET /users
List all users (Admin only).

**Response:**
```json
{
  "users": [
    {
      "user_id": "user_123",
      "email": "john.doe@example.com",
      "name": "John Doe",
      "role": "reviewer",
      "projects": ["proj_123", "proj_124"],
      "last_login": "2024-01-20T14:30:00Z",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 25
}
```

### POST /users/{user_id}/role
Update user role (Admin only).

**Request Body:**
```json
{
  "role": "admin"
}
```

**Response:**
```json
{
  "user_id": "user_123",
  "role": "admin",
  "updated_at": "2024-01-20T18:30:00Z"
}
```

## Audit Logs

### GET /audit/logs
Get audit logs (Admin only).

**Query Parameters:**
- `user_id`: Filter by user
- `action`: Filter by action type
- `start_date`: Start date (ISO 8601)
- `end_date`: End date (ISO 8601)
- `page`: Page number
- `per_page`: Items per page

**Response:**
```json
{
  "logs": [
    {
      "log_id": "log_456",
      "timestamp": "2024-01-20T18:30:45Z",
      "user_id": "user_123",
      "user_email": "john.doe@example.com",
      "action": "document_downloaded",
      "resource_type": "document",
      "resource_id": "doc_456",
      "ip_address": "203.0.113.42",
      "user_agent": "Mozilla/5.0...",
      "details": {
        "document_name": "PPA_Agreement.pdf",
        "project_id": "proj_123"
      }
    }
  ],
  "total": 1250,
  "page": 1,
  "per_page": 50
}
```

## Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "capacity_mw",
      "issue": "Must be a positive number"
    }
  }
}
```

### Error Codes
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid or missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `409` - Conflict (duplicate resource)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

## Rate Limiting

- **Per minute**: 60 requests
- **Per hour**: 1000 requests

Rate limit headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705776000
```

## Webhooks (Optional)

Configure webhooks to receive real-time notifications.

### Events
- `document.uploaded`
- `document.processed`
- `checklist.item.completed`
- `issue.created`
- `project.completed`

### Webhook Payload Example
```json
{
  "event": "document.processed",
  "timestamp": "2024-01-20T16:32:15Z",
  "data": {
    "document_id": "doc_456",
    "project_id": "proj_123",
    "document_type": "ppa",
    "status": "processed"
  }
}
```

## SDKs and Client Libraries

Official client libraries available for:
- Python: `pip install renewable-dd-client`
- JavaScript/TypeScript: `npm install @renewable-dd/client`
- Go: `go get github.com/renewable-dd/go-client`

## Support

- API Status: https://status.your-domain.com
- Documentation: https://docs.your-domain.com
- Support Email: api-support@your-domain.com

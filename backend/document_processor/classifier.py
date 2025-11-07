"""
Document classification system for renewable energy DD documents
Automatically identifies document types using LLM and rule-based approaches
"""
from typing import Dict, Any, List, Tuple, Optional
from enum import Enum
import re
import structlog
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from api.config import settings

logger = structlog.get_logger()


class DocumentType(str, Enum):
    """Standard renewable energy DD document types"""
    # Commercial
    PPA = "ppa"  # Power Purchase Agreement
    OFFTAKE_AGREEMENT = "offtake_agreement"
    MERCHANT_AGREEMENT = "merchant_agreement"

    # Legal
    LAND_LEASE = "land_lease"
    EASEMENT = "easement"
    DEVELOPMENT_AGREEMENT = "development_agreement"
    EPC_CONTRACT = "epc_contract"
    CORPORATE_DOCS = "corporate_documents"

    # Technical
    INTERCONNECTION_AGREEMENT = "interconnection_agreement"
    INTERCONNECTION_STUDY = "interconnection_study"
    TECHNICAL_SPECS = "technical_specifications"
    EQUIPMENT_SPECS = "equipment_specifications"
    PRODUCTION_DATA = "production_data"
    RESOURCE_ASSESSMENT = "resource_assessment"

    # O&M
    OM_CONTRACT = "om_contract"
    EQUIPMENT_WARRANTY = "equipment_warranty"
    SERVICE_AGREEMENT = "service_agreement"

    # Environmental
    ENVIRONMENTAL_ASSESSMENT = "environmental_assessment"
    ENVIRONMENTAL_PERMIT = "environmental_permit"
    ENVIRONMENTAL_STUDY = "environmental_study"

    # Financial
    FINANCIAL_MODEL = "financial_model"
    AUDIT_REPORT = "audit_report"
    TAX_DOCUMENT = "tax_document"
    INSURANCE_POLICY = "insurance_policy"
    DEBT_AGREEMENT = "debt_agreement"
    TAX_EQUITY_DOCS = "tax_equity_documents"

    # Permits and Approvals
    BUILDING_PERMIT = "building_permit"
    ZONING_APPROVAL = "zoning_approval"
    REGULATORY_APPROVAL = "regulatory_approval"

    # Other
    TITLE_REPORT = "title_report"
    APPRAISAL = "appraisal"
    PHASE_I_ESA = "phase_i_esa"
    UNKNOWN = "unknown"


class DocumentCategory(str, Enum):
    """High-level document categories"""
    LEGAL = "Legal"
    TECHNICAL = "Technical"
    FINANCIAL = "Financial"
    ENVIRONMENTAL = "Environmental"
    COMMERCIAL = "Commercial"


# Mapping of document types to categories
DOCUMENT_TYPE_TO_CATEGORY = {
    DocumentType.PPA: DocumentCategory.COMMERCIAL,
    DocumentType.OFFTAKE_AGREEMENT: DocumentCategory.COMMERCIAL,
    DocumentType.MERCHANT_AGREEMENT: DocumentCategory.COMMERCIAL,

    DocumentType.LAND_LEASE: DocumentCategory.LEGAL,
    DocumentType.EASEMENT: DocumentCategory.LEGAL,
    DocumentType.DEVELOPMENT_AGREEMENT: DocumentCategory.LEGAL,
    DocumentType.EPC_CONTRACT: DocumentCategory.LEGAL,
    DocumentType.CORPORATE_DOCS: DocumentCategory.LEGAL,

    DocumentType.INTERCONNECTION_AGREEMENT: DocumentCategory.TECHNICAL,
    DocumentType.INTERCONNECTION_STUDY: DocumentCategory.TECHNICAL,
    DocumentType.TECHNICAL_SPECS: DocumentCategory.TECHNICAL,
    DocumentType.EQUIPMENT_SPECS: DocumentCategory.TECHNICAL,
    DocumentType.PRODUCTION_DATA: DocumentCategory.TECHNICAL,
    DocumentType.RESOURCE_ASSESSMENT: DocumentCategory.TECHNICAL,

    DocumentType.OM_CONTRACT: DocumentCategory.TECHNICAL,
    DocumentType.EQUIPMENT_WARRANTY: DocumentCategory.TECHNICAL,
    DocumentType.SERVICE_AGREEMENT: DocumentCategory.TECHNICAL,

    DocumentType.ENVIRONMENTAL_ASSESSMENT: DocumentCategory.ENVIRONMENTAL,
    DocumentType.ENVIRONMENTAL_PERMIT: DocumentCategory.ENVIRONMENTAL,
    DocumentType.ENVIRONMENTAL_STUDY: DocumentCategory.ENVIRONMENTAL,
    DocumentType.PHASE_I_ESA: DocumentCategory.ENVIRONMENTAL,

    DocumentType.FINANCIAL_MODEL: DocumentCategory.FINANCIAL,
    DocumentType.AUDIT_REPORT: DocumentCategory.FINANCIAL,
    DocumentType.TAX_DOCUMENT: DocumentCategory.FINANCIAL,
    DocumentType.INSURANCE_POLICY: DocumentCategory.FINANCIAL,
    DocumentType.DEBT_AGREEMENT: DocumentCategory.FINANCIAL,
    DocumentType.TAX_EQUITY_DOCS: DocumentCategory.FINANCIAL,

    DocumentType.BUILDING_PERMIT: DocumentCategory.LEGAL,
    DocumentType.ZONING_APPROVAL: DocumentCategory.LEGAL,
    DocumentType.REGULATORY_APPROVAL: DocumentCategory.LEGAL,
    DocumentType.TITLE_REPORT: DocumentCategory.LEGAL,
    DocumentType.APPRAISAL: DocumentCategory.FINANCIAL,
}


class DocumentClassifier:
    """Classifier for renewable energy DD documents"""

    # Keywords for rule-based classification
    CLASSIFICATION_KEYWORDS = {
        DocumentType.PPA: [
            "power purchase agreement", "ppa", "offtaker", "renewable energy credit",
            "rec", "energy price", "$/mwh", "delivery point", "contract capacity"
        ],
        DocumentType.INTERCONNECTION_AGREEMENT: [
            "interconnection agreement", "interconnection service", "transmission provider",
            "network upgrade", "point of interconnection", "poi", "system impact study"
        ],
        DocumentType.LAND_LEASE: [
            "land lease", "lessor", "lessee", "rental payment", "lease term",
            "real property", "premises", "lease agreement"
        ],
        DocumentType.ENVIRONMENTAL_PERMIT: [
            "environmental permit", "air quality permit", "water discharge permit",
            "epa", "environmental protection", "permit conditions"
        ],
        DocumentType.EQUIPMENT_WARRANTY: [
            "warranty", "manufacturer", "defects", "warranty period",
            "performance guarantee", "warranty claim"
        ],
        DocumentType.OM_CONTRACT: [
            "operation and maintenance", "o&m", "maintenance services",
            "availability guarantee", "maintenance schedule"
        ],
        DocumentType.FINANCIAL_MODEL: [
            "financial model", "irr", "internal rate of return", "npv",
            "cash flow", "project finance", "pro forma"
        ],
        DocumentType.RESOURCE_ASSESSMENT: [
            "resource assessment", "wind resource", "solar resource",
            "capacity factor", "p50", "p90", "energy yield"
        ],
    }

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY
        )

        self.classification_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert in renewable energy due diligence documentation.
            Classify the following document excerpt into one of these categories:

            {document_types}

            Respond with ONLY the document type identifier (e.g., 'ppa', 'interconnection_agreement', etc.)
            followed by a confidence score (0-1) on the next line.

            Format:
            document_type
            confidence_score
            """),
            ("user", "Document Title: {title}\n\nDocument Excerpt:\n{excerpt}")
        ])

    def classify_by_keywords(
        self,
        text: str,
        filename: str = ""
    ) -> Tuple[DocumentType, float]:
        """
        Rule-based classification using keywords

        Args:
            text: Document text content
            filename: Document filename

        Returns:
            Tuple of (document_type, confidence_score)
        """
        text_lower = text.lower()
        filename_lower = filename.lower()
        combined_text = f"{filename_lower} {text_lower}"

        scores = {}

        for doc_type, keywords in self.CLASSIFICATION_KEYWORDS.items():
            score = 0
            matched_keywords = 0

            for keyword in keywords:
                if keyword in combined_text:
                    matched_keywords += 1
                    # Weight filename matches higher
                    if keyword in filename_lower:
                        score += 2
                    else:
                        score += 1

            if matched_keywords > 0:
                # Normalize score
                scores[doc_type] = min(score / (len(keywords) * 1.5), 1.0)

        if scores:
            best_type = max(scores, key=scores.get)
            confidence = scores[best_type]
            logger.info(f"Keyword classification: {best_type.value} (confidence: {confidence:.2f})")
            return best_type, confidence

        return DocumentType.UNKNOWN, 0.0

    async def classify_with_llm(
        self,
        text: str,
        title: str = ""
    ) -> Tuple[DocumentType, float]:
        """
        LLM-based classification

        Args:
            text: Document text content
            title: Document title/filename

        Returns:
            Tuple of (document_type, confidence_score)
        """
        try:
            # Get first 2000 characters for classification
            excerpt = text[:2000]

            # Prepare document types for prompt
            doc_types_str = "\n".join([
                f"- {dt.value}: {dt.name.replace('_', ' ').title()}"
                for dt in DocumentType if dt != DocumentType.UNKNOWN
            ])

            # Create prompt
            messages = self.classification_prompt.format_messages(
                document_types=doc_types_str,
                title=title,
                excerpt=excerpt
            )

            # Get response
            response = await self.llm.ainvoke(messages)
            result = response.content.strip().split('\n')

            if len(result) >= 2:
                doc_type_str = result[0].strip().lower()
                confidence = float(result[1].strip())

                # Map to DocumentType
                try:
                    doc_type = DocumentType(doc_type_str)
                    logger.info(f"LLM classification: {doc_type.value} (confidence: {confidence:.2f})")
                    return doc_type, confidence
                except ValueError:
                    logger.warning(f"Unknown document type from LLM: {doc_type_str}")
                    return DocumentType.UNKNOWN, 0.0

        except Exception as e:
            logger.error(f"LLM classification failed: {str(e)}")
            return DocumentType.UNKNOWN, 0.0

        return DocumentType.UNKNOWN, 0.0

    async def classify_document(
        self,
        text: str,
        filename: str = "",
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """
        Classify document using hybrid approach (keywords + LLM)

        Args:
            text: Document text content
            filename: Document filename
            use_llm: Whether to use LLM for classification

        Returns:
            Classification result with type, category, and confidence
        """
        # Try keyword-based classification first
        keyword_type, keyword_confidence = self.classify_by_keywords(text, filename)

        # If keyword confidence is high enough, use it
        if keyword_confidence >= settings.MIN_CLASSIFICATION_CONFIDENCE:
            doc_type = keyword_type
            confidence = keyword_confidence
            method = "keywords"
        elif use_llm:
            # Use LLM classification
            llm_type, llm_confidence = await self.classify_with_llm(text, filename)

            # Choose best classification
            if llm_confidence > keyword_confidence:
                doc_type = llm_type
                confidence = llm_confidence
                method = "llm"
            else:
                doc_type = keyword_type
                confidence = keyword_confidence
                method = "keywords"
        else:
            doc_type = keyword_type
            confidence = keyword_confidence
            method = "keywords"

        # Get category
        category = DOCUMENT_TYPE_TO_CATEGORY.get(doc_type, None)

        result = {
            "document_type": doc_type.value,
            "category": category.value if category else None,
            "confidence": round(confidence, 3),
            "classification_method": method,
            "requires_review": confidence < settings.MIN_CLASSIFICATION_CONFIDENCE
        }

        logger.info(
            "Document classified",
            document_type=result["document_type"],
            confidence=result["confidence"],
            method=method
        )

        return result

    def get_category_for_type(self, doc_type: DocumentType) -> Optional[DocumentCategory]:
        """Get category for a document type"""
        return DOCUMENT_TYPE_TO_CATEGORY.get(doc_type)


# Global classifier instance
document_classifier = DocumentClassifier()

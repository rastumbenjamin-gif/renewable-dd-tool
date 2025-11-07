"""
Industry-standard Due Diligence checklist for renewable energy projects
Comprehensive checklist covering all aspects of DD for solar, wind, hydro, and battery storage
"""
from typing import List, Dict, Any
from enum import Enum
from pydantic import BaseModel


class ChecklistItemStatus(str, Enum):
    """Status of checklist items"""
    NOT_STARTED = "not_started"
    PENDING = "pending"  # Waiting for seller
    RECEIVED = "received"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NOT_APPLICABLE = "not_applicable"


class Priority(str, Enum):
    """Priority levels for checklist items"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ResponsibleParty(str, Enum):
    """Who is responsible for providing/reviewing"""
    SELLER = "seller"
    BUYER = "buyer"
    THIRD_PARTY = "third_party"


class ChecklistItem(BaseModel):
    """Individual checklist item"""
    id: str
    category: str
    subcategory: str
    item_name: str
    description: str
    priority: Priority
    responsible_party: ResponsibleParty
    status: ChecklistItemStatus = ChecklistItemStatus.NOT_STARTED
    document_ids: List[str] = []  # Associated document IDs
    notes: str = ""
    reviewer_comments: str = ""
    requires_legal_review: bool = False
    requires_technical_review: bool = False
    requires_financial_review: bool = False


# Standard Renewable Energy DD Checklist
RENEWABLE_DD_CHECKLIST: List[Dict[str, Any]] = [
    # ====================
    # LEGAL & CORPORATE
    # ====================
    {
        "id": "legal_001",
        "category": "Legal",
        "subcategory": "Corporate Structure",
        "item_name": "Articles of Incorporation/Formation",
        "description": "Certified copies of articles of incorporation or formation",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_legal_review": True
    },
    {
        "id": "legal_002",
        "category": "Legal",
        "subcategory": "Corporate Structure",
        "item_name": "Operating Agreement/Bylaws",
        "description": "Current operating agreement or corporate bylaws",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_legal_review": True
    },
    {
        "id": "legal_003",
        "category": "Legal",
        "subcategory": "Corporate Structure",
        "item_name": "Corporate Good Standing",
        "description": "Certificates of good standing from state of formation",
        "priority": Priority.HIGH,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_legal_review": True
    },
    {
        "id": "legal_004",
        "category": "Legal",
        "subcategory": "Corporate Structure",
        "item_name": "Ownership Structure",
        "description": "Detailed ownership structure and cap table",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_legal_review": True
    },

    # Permits and Approvals
    {
        "id": "legal_005",
        "category": "Legal",
        "subcategory": "Permits",
        "item_name": "Building Permits",
        "description": "All building and construction permits",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_legal_review": True
    },
    {
        "id": "legal_006",
        "category": "Legal",
        "subcategory": "Permits",
        "item_name": "Zoning Approvals",
        "description": "Zoning approvals and variances",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_legal_review": True
    },
    {
        "id": "legal_007",
        "category": "Legal",
        "subcategory": "Permits",
        "item_name": "Environmental Permits",
        "description": "All environmental permits (air, water, etc.)",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_legal_review": True
    },

    # Real Property
    {
        "id": "legal_008",
        "category": "Legal",
        "subcategory": "Real Property",
        "item_name": "Land Lease Agreements",
        "description": "All land lease agreements with landowners",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_legal_review": True
    },
    {
        "id": "legal_009",
        "category": "Legal",
        "subcategory": "Real Property",
        "item_name": "Easement Agreements",
        "description": "Transmission, access, and other easement agreements",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_legal_review": True
    },
    {
        "id": "legal_010",
        "category": "Legal",
        "subcategory": "Real Property",
        "item_name": "Title Reports",
        "description": "Title insurance policies and updated title reports",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_legal_review": True
    },
    {
        "id": "legal_011",
        "category": "Legal",
        "subcategory": "Real Property",
        "item_name": "Surveys",
        "description": "ALTA surveys of project property",
        "priority": Priority.HIGH,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_technical_review": True
    },

    # ====================
    # COMMERCIAL
    # ====================
    {
        "id": "comm_001",
        "category": "Commercial",
        "subcategory": "Offtake",
        "item_name": "Power Purchase Agreement",
        "description": "Executed PPA with offtaker including all amendments",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_legal_review": True,
        "requires_financial_review": True
    },
    {
        "id": "comm_002",
        "category": "Commercial",
        "subcategory": "Offtake",
        "item_name": "Offtaker Credit Analysis",
        "description": "Credit rating and financial analysis of offtaker",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.BUYER,
        "requires_financial_review": True
    },
    {
        "id": "comm_003",
        "category": "Commercial",
        "subcategory": "Offtake",
        "item_name": "REC Purchase Agreement",
        "description": "Renewable energy credit purchase agreements if separate",
        "priority": Priority.HIGH,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_legal_review": True
    },

    # ====================
    # TECHNICAL
    # ====================
    {
        "id": "tech_001",
        "category": "Technical",
        "subcategory": "Interconnection",
        "item_name": "Interconnection Agreement",
        "description": "Executed interconnection agreement with utility",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_legal_review": True,
        "requires_technical_review": True
    },
    {
        "id": "tech_002",
        "category": "Technical",
        "subcategory": "Interconnection",
        "item_name": "System Impact Study",
        "description": "Completed system impact study",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_technical_review": True
    },
    {
        "id": "tech_003",
        "category": "Technical",
        "subcategory": "Interconnection",
        "item_name": "Facilities Study",
        "description": "Completed facilities study with cost estimates",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_technical_review": True,
        "requires_financial_review": True
    },
    {
        "id": "tech_004",
        "category": "Technical",
        "subcategory": "Interconnection",
        "item_name": "Queue Position",
        "description": "Documentation of interconnection queue position",
        "priority": Priority.HIGH,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_technical_review": True
    },

    # Resource Assessment
    {
        "id": "tech_005",
        "category": "Technical",
        "subcategory": "Resource Assessment",
        "item_name": "Resource Assessment Report",
        "description": "Independent resource assessment (wind/solar/hydro)",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_technical_review": True
    },
    {
        "id": "tech_006",
        "category": "Technical",
        "subcategory": "Resource Assessment",
        "item_name": "P50/P90 Production Estimates",
        "description": "Long-term energy production estimates",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_technical_review": True,
        "requires_financial_review": True
    },
    {
        "id": "tech_007",
        "category": "Technical",
        "subcategory": "Resource Assessment",
        "item_name": "Historical Meteorological Data",
        "description": "On-site met tower or satellite data",
        "priority": Priority.HIGH,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_technical_review": True
    },

    # Equipment
    {
        "id": "tech_008",
        "category": "Technical",
        "subcategory": "Equipment",
        "item_name": "Equipment Specifications",
        "description": "Technical specifications for all major equipment",
        "priority": Priority.HIGH,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_technical_review": True
    },
    {
        "id": "tech_009",
        "category": "Technical",
        "subcategory": "Equipment",
        "item_name": "Equipment Warranties",
        "description": "Manufacturer warranties for panels/turbines/batteries",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_legal_review": True,
        "requires_technical_review": True
    },
    {
        "id": "tech_010",
        "category": "Technical",
        "subcategory": "Equipment",
        "item_name": "Performance Guarantees",
        "description": "Equipment performance guarantees and test results",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_technical_review": True
    },
    {
        "id": "tech_011",
        "category": "Technical",
        "subcategory": "Equipment",
        "item_name": "Supply Agreements",
        "description": "Equipment purchase and supply agreements",
        "priority": Priority.HIGH,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_legal_review": True
    },

    # O&M
    {
        "id": "tech_012",
        "category": "Technical",
        "subcategory": "Operations & Maintenance",
        "item_name": "O&M Agreement",
        "description": "Operations and maintenance service agreement",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_legal_review": True,
        "requires_financial_review": True
    },
    {
        "id": "tech_013",
        "category": "Technical",
        "subcategory": "Operations & Maintenance",
        "item_name": "O&M Budget",
        "description": "Detailed O&M cost estimates and budget",
        "priority": Priority.HIGH,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_financial_review": True
    },

    # Design and Engineering
    {
        "id": "tech_014",
        "category": "Technical",
        "subcategory": "Design",
        "item_name": "Engineering Design",
        "description": "Complete engineering design package",
        "priority": Priority.HIGH,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_technical_review": True
    },
    {
        "id": "tech_015",
        "category": "Technical",
        "subcategory": "Design",
        "item_name": "Single Line Diagrams",
        "description": "Electrical single line diagrams",
        "priority": Priority.MEDIUM,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_technical_review": True
    },

    # ====================
    # FINANCIAL
    # ====================
    {
        "id": "fin_001",
        "category": "Financial",
        "subcategory": "Financial Model",
        "item_name": "Financial Model",
        "description": "Complete project financial model",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_financial_review": True
    },
    {
        "id": "fin_002",
        "category": "Financial",
        "subcategory": "Financial Model",
        "item_name": "Model Assumptions",
        "description": "Documentation of all model assumptions",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_financial_review": True
    },
    {
        "id": "fin_003",
        "category": "Financial",
        "subcategory": "Financial Model",
        "item_name": "Sensitivity Analysis",
        "description": "Sensitivity analysis on key variables",
        "priority": Priority.HIGH,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_financial_review": True
    },

    # Financial Statements
    {
        "id": "fin_004",
        "category": "Financial",
        "subcategory": "Financial Statements",
        "item_name": "Audited Financial Statements",
        "description": "Audited financials for past 3 years",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_financial_review": True
    },
    {
        "id": "fin_005",
        "category": "Financial",
        "subcategory": "Financial Statements",
        "item_name": "Interim Financial Statements",
        "description": "Unaudited interim financial statements",
        "priority": Priority.HIGH,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_financial_review": True
    },

    # Tax
    {
        "id": "fin_006",
        "category": "Financial",
        "subcategory": "Tax",
        "item_name": "ITC/PTC Documentation",
        "description": "Investment or Production Tax Credit documentation",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_legal_review": True,
        "requires_financial_review": True
    },
    {
        "id": "fin_007",
        "category": "Financial",
        "subcategory": "Tax",
        "item_name": "Tax Equity Structure",
        "description": "Tax equity partnership/flip structure documents",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_legal_review": True,
        "requires_financial_review": True
    },
    {
        "id": "fin_008",
        "category": "Financial",
        "subcategory": "Tax",
        "item_name": "Tax Returns",
        "description": "Federal and state tax returns for past 3 years",
        "priority": Priority.HIGH,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_financial_review": True
    },

    # Debt and Financing
    {
        "id": "fin_009",
        "category": "Financial",
        "subcategory": "Debt",
        "item_name": "Debt Agreements",
        "description": "All debt agreements and loan documents",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_legal_review": True,
        "requires_financial_review": True
    },
    {
        "id": "fin_010",
        "category": "Financial",
        "subcategory": "Debt",
        "item_name": "Debt Service Schedule",
        "description": "Debt service payment schedule",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_financial_review": True
    },

    # Insurance
    {
        "id": "fin_011",
        "category": "Financial",
        "subcategory": "Insurance",
        "item_name": "Insurance Policies",
        "description": "All current insurance policies",
        "priority": Priority.HIGH,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_legal_review": True
    },
    {
        "id": "fin_012",
        "category": "Financial",
        "subcategory": "Insurance",
        "item_name": "Insurance Claims History",
        "description": "History of insurance claims",
        "priority": Priority.MEDIUM,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_financial_review": True
    },

    # ====================
    # ENVIRONMENTAL
    # ====================
    {
        "id": "env_001",
        "category": "Environmental",
        "subcategory": "Environmental Assessment",
        "item_name": "Phase I Environmental Site Assessment",
        "description": "Phase I ESA per ASTM standards",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_technical_review": True
    },
    {
        "id": "env_002",
        "category": "Environmental",
        "subcategory": "Environmental Assessment",
        "item_name": "Phase II ESA (if required)",
        "description": "Phase II environmental assessment if contamination found",
        "priority": Priority.CRITICAL,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_technical_review": True
    },
    {
        "id": "env_003",
        "category": "Environmental",
        "subcategory": "Environmental Assessment",
        "item_name": "Wetlands Delineation",
        "description": "Wetlands delineation and jurisdictional determination",
        "priority": Priority.HIGH,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_technical_review": True
    },
    {
        "id": "env_004",
        "category": "Environmental",
        "subcategory": "Environmental Assessment",
        "item_name": "Endangered Species Assessment",
        "description": "Threatened and endangered species survey",
        "priority": Priority.HIGH,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_technical_review": True
    },
    {
        "id": "env_005",
        "category": "Environmental",
        "subcategory": "Environmental Assessment",
        "item_name": "Archaeological/Cultural Survey",
        "description": "Cultural resources and archaeological assessment",
        "priority": Priority.HIGH,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_technical_review": True
    },

    # Environmental Compliance
    {
        "id": "env_006",
        "category": "Environmental",
        "subcategory": "Compliance",
        "item_name": "Environmental Compliance Records",
        "description": "History of environmental compliance and violations",
        "priority": Priority.HIGH,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_legal_review": True
    },
    {
        "id": "env_007",
        "category": "Environmental",
        "subcategory": "Compliance",
        "item_name": "Mitigation Plans",
        "description": "Environmental mitigation and monitoring plans",
        "priority": Priority.MEDIUM,
        "responsible_party": ResponsibleParty.SELLER,
        "requires_technical_review": True
    },
]


class DDChecklistManager:
    """Manager for DD checklist"""

    def __init__(self):
        self.checklist_items = self._initialize_checklist()

    def _initialize_checklist(self) -> List[ChecklistItem]:
        """Initialize checklist from template"""
        return [ChecklistItem(**item) for item in RENEWABLE_DD_CHECKLIST]

    def get_checklist(self, category: str = None) -> List[ChecklistItem]:
        """Get checklist items, optionally filtered by category"""
        if category:
            return [item for item in self.checklist_items if item.category == category]
        return self.checklist_items

    def get_completion_stats(self) -> Dict[str, Any]:
        """Get completion statistics"""
        total = len(self.checklist_items)
        completed = sum(1 for item in self.checklist_items if item.status == ChecklistItemStatus.APPROVED)

        by_category = {}
        for item in self.checklist_items:
            if item.category not in by_category:
                by_category[item.category] = {"total": 0, "completed": 0}
            by_category[item.category]["total"] += 1
            if item.status == ChecklistItemStatus.APPROVED:
                by_category[item.category]["completed"] += 1

        return {
            "total_items": total,
            "completed_items": completed,
            "completion_percentage": round((completed / total) * 100, 1) if total > 0 else 0,
            "by_category": by_category
        }

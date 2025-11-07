"""
Executive Summary Generator
Generates comprehensive executive summaries of DD status and findings
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from api.config import settings
from models.dd_checklist import DDChecklistManager, ChecklistItemStatus

logger = structlog.get_logger()


class ExecutiveSummaryGenerator:
    """Generator for executive DD summaries"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.3,  # Slightly higher for more natural text
            api_key=settings.OPENAI_API_KEY
        )

        self.summary_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert renewable energy investment advisor creating executive summaries for due diligence.

            Create a concise, professional executive summary that includes:
            1. Project Overview (technology, capacity, location)
            2. Due Diligence Status
            3. Key Findings (positive and negative)
            4. Critical Risks and Red Flags
            5. Deal Breakers (if any)
            6. Recommended Next Steps

            Use clear, executive-level language. Be direct about risks.
            Format in markdown with clear sections.
            """),
            ("user", """Create an executive summary for this renewable energy project DD:

Project Information:
{project_info}

DD Completion Status:
{completion_status}

Key Documents Reviewed:
{documents_summary}

Extracted Terms and Findings:
{findings}

Issues and Red Flags:
{issues}
""")
        ])

    async def generate_summary(
        self,
        project_data: Dict[str, Any],
        checklist_status: Dict[str, Any],
        key_findings: List[Dict[str, Any]],
        issues: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate executive summary

        Args:
            project_data: Project information
            checklist_status: DD checklist completion status
            key_findings: Key findings from document review
            issues: Issues and red flags identified

        Returns:
            Executive summary with metrics and narrative
        """
        try:
            # Prepare inputs
            project_info = self._format_project_info(project_data)
            completion_status = self._format_completion_status(checklist_status)
            documents_summary = self._format_documents_summary(key_findings)
            findings_text = self._format_findings(key_findings)
            issues_text = self._format_issues(issues)

            # Generate narrative summary using LLM
            messages = self.summary_prompt.format_messages(
                project_info=project_info,
                completion_status=completion_status,
                documents_summary=documents_summary,
                findings=findings_text,
                issues=issues_text
            )

            response = await self.llm.ainvoke(messages)
            narrative = response.content

            # Calculate metrics
            metrics = self._calculate_metrics(
                project_data,
                checklist_status,
                issues
            )

            # Identify deal breakers
            deal_breakers = self._identify_deal_breakers(issues)

            # Generate action items
            action_items = self._generate_action_items(
                checklist_status,
                issues
            )

            summary = {
                "generated_at": datetime.utcnow().isoformat(),
                "narrative": narrative,
                "metrics": metrics,
                "deal_breakers": deal_breakers,
                "action_items": action_items,
                "overall_risk_rating": self._calculate_risk_rating(issues, metrics),
                "recommendation": self._generate_recommendation(
                    deal_breakers,
                    issues,
                    metrics
                )
            }

            logger.info("Executive summary generated successfully")
            return summary

        except Exception as e:
            logger.error(f"Failed to generate executive summary: {str(e)}")
            raise

    def _format_project_info(self, project_data: Dict[str, Any]) -> str:
        """Format project information"""
        info = []
        info.append(f"Project Name: {project_data.get('name', 'N/A')}")
        info.append(f"Technology: {project_data.get('technology_type', 'N/A')}")
        info.append(f"Capacity: {project_data.get('capacity_mw', 'N/A')} MW")
        info.append(f"Location: {project_data.get('location', 'N/A')}")
        info.append(f"Expected COD: {project_data.get('cod', 'N/A')}")

        if project_data.get('ppa_terms'):
            ppa = project_data['ppa_terms']
            info.append(f"PPA Price: {ppa.get('energy_price', 'N/A')}")
            info.append(f"PPA Term: {ppa.get('delivery_term_years', 'N/A')} years")
            info.append(f"Offtaker: {ppa.get('buyer', 'N/A')}")

        return "\n".join(info)

    def _format_completion_status(self, status: Dict[str, Any]) -> str:
        """Format completion status"""
        lines = []
        lines.append(f"Overall Completion: {status.get('completion_percentage', 0)}%")
        lines.append(f"Total Items: {status.get('total_items', 0)}")
        lines.append(f"Completed: {status.get('completed_items', 0)}")

        if status.get('by_category'):
            lines.append("\nBy Category:")
            for category, cat_status in status['by_category'].items():
                pct = (cat_status['completed'] / cat_status['total'] * 100) if cat_status['total'] > 0 else 0
                lines.append(f"  {category}: {pct:.0f}% ({cat_status['completed']}/{cat_status['total']})")

        return "\n".join(lines)

    def _format_documents_summary(self, findings: List[Dict[str, Any]]) -> str:
        """Format documents summary"""
        if not findings:
            return "No documents reviewed yet."

        doc_types = {}
        for finding in findings:
            doc_type = finding.get('document_type', 'Unknown')
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1

        lines = [f"{count} {doc_type} document(s)" for doc_type, count in doc_types.items()]
        return "\n".join(lines)

    def _format_findings(self, findings: List[Dict[str, Any]]) -> str:
        """Format key findings"""
        if not findings:
            return "No significant findings yet."

        lines = []
        for i, finding in enumerate(findings[:10], 1):  # Top 10 findings
            lines.append(f"{i}. {finding.get('summary', 'N/A')}")

        return "\n".join(lines)

    def _format_issues(self, issues: List[Dict[str, Any]]) -> str:
        """Format issues and red flags"""
        if not issues:
            return "No issues identified."

        lines = []
        for issue in issues:
            severity = issue.get('severity', 'Medium').upper()
            description = issue.get('description', 'N/A')
            lines.append(f"[{severity}] {description}")

        return "\n".join(lines)

    def _calculate_metrics(
        self,
        project_data: Dict[str, Any],
        checklist_status: Dict[str, Any],
        issues: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate key metrics"""
        metrics = {
            "completion_percentage": checklist_status.get('completion_percentage', 0),
            "documents_reviewed": checklist_status.get('completed_items', 0),
            "total_documents_required": checklist_status.get('total_items', 0),
            "critical_issues": len([i for i in issues if i.get('severity') == 'Critical']),
            "high_issues": len([i for i in issues if i.get('severity') == 'High']),
            "medium_issues": len([i for i in issues if i.get('severity') == 'Medium']),
            "total_issues": len(issues)
        }

        # Project-specific metrics
        if project_data.get('capacity_mw') and project_data.get('ppa_terms'):
            ppa = project_data['ppa_terms']
            if ppa.get('energy_price'):
                import re
                price_match = re.search(r'\$?(\d+\.?\d*)', ppa['energy_price'])
                if price_match:
                    price = float(price_match.group(1))
                    capacity = float(project_data['capacity_mw'])
                    term = int(ppa.get('delivery_term_years', 20))

                    # Estimate lifetime revenue (simplified)
                    annual_energy = capacity * 8760 * 0.30  # 30% capacity factor
                    annual_revenue = annual_energy * price
                    lifetime_revenue = annual_revenue * term

                    metrics['estimated_lifetime_revenue_usd'] = int(lifetime_revenue)
                    metrics['estimated_annual_revenue_usd'] = int(annual_revenue)

        return metrics

    def _identify_deal_breakers(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Identify potential deal breakers"""
        deal_breakers = []

        critical_issues = [i for i in issues if i.get('severity') == 'Critical']

        deal_breaker_keywords = [
            'no interconnection agreement',
            'no ppa',
            'land lease expired',
            'no environmental permit',
            'title issue',
            'litigation',
            'bankruptcy',
            'force majeure',
            'terminated'
        ]

        for issue in critical_issues:
            description = issue.get('description', '').lower()
            for keyword in deal_breaker_keywords:
                if keyword in description:
                    deal_breakers.append(issue.get('description'))
                    break

        return deal_breakers

    def _generate_action_items(
        self,
        checklist_status: Dict[str, Any],
        issues: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Generate recommended action items"""
        action_items = []

        # Incomplete critical items
        if checklist_status.get('completion_percentage', 0) < 100:
            action_items.append({
                "priority": "High",
                "action": "Complete outstanding DD checklist items",
                "owner": "Seller",
                "deadline": "Before closing"
            })

        # Critical issues
        critical_issues = [i for i in issues if i.get('severity') == 'Critical']
        for issue in critical_issues[:3]:  # Top 3 critical issues
            action_items.append({
                "priority": "Critical",
                "action": f"Resolve: {issue.get('description', 'N/A')[:100]}",
                "owner": "Seller",
                "deadline": "Immediate"
            })

        # Standard next steps
        if checklist_status.get('completion_percentage', 0) > 75:
            action_items.append({
                "priority": "Medium",
                "action": "Schedule technical site visit",
                "owner": "Buyer",
                "deadline": "Next 2 weeks"
            })

            action_items.append({
                "priority": "Medium",
                "action": "Engage independent engineer for technical review",
                "owner": "Buyer",
                "deadline": "Next 2 weeks"
            })

        return action_items

    def _calculate_risk_rating(
        self,
        issues: List[Dict[str, Any]],
        metrics: Dict[str, Any]
    ) -> str:
        """Calculate overall risk rating"""
        critical_count = metrics.get('critical_issues', 0)
        high_count = metrics.get('high_issues', 0)
        completion = metrics.get('completion_percentage', 0)

        if critical_count > 3 or completion < 50:
            return "HIGH"
        elif critical_count > 0 or high_count > 5 or completion < 75:
            return "MEDIUM"
        elif high_count > 0 or completion < 90:
            return "MEDIUM-LOW"
        else:
            return "LOW"

    def _generate_recommendation(
        self,
        deal_breakers: List[str],
        issues: List[Dict[str, Any]],
        metrics: Dict[str, Any]
    ) -> str:
        """Generate overall recommendation"""
        if deal_breakers:
            return "DO NOT PROCEED - Critical deal breakers identified"

        critical_count = metrics.get('critical_issues', 0)
        completion = metrics.get('completion_percentage', 0)

        if critical_count > 3:
            return "CAUTION - Multiple critical issues require resolution before proceeding"
        elif completion < 70:
            return "CONTINUE DD - Substantial information still required"
        elif completion > 90 and critical_count == 0:
            return "PROCEED TO CLOSING - DD substantially complete with manageable risks"
        else:
            return "CONTINUE DD - Complete outstanding items and address identified issues"


# Global summary generator instance
summary_generator = ExecutiveSummaryGenerator()

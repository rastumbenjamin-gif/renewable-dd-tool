"""
Power Purchase Agreement (PPA) extractor
Extracts key terms, pricing, and obligations from PPAs
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import re
import structlog
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from api.config import settings

logger = structlog.get_logger()


class PPATerms(BaseModel):
    """Structured PPA terms"""
    # Parties
    seller: Optional[str] = Field(None, description="Energy seller/generator")
    buyer: Optional[str] = Field(None, description="Energy buyer/offtaker")

    # Project Information
    project_name: Optional[str] = Field(None, description="Project name")
    project_location: Optional[str] = Field(None, description="Project location")
    technology_type: Optional[str] = Field(None, description="Technology (solar, wind, etc.)")
    contract_capacity_mw: Optional[float] = Field(None, description="Contract capacity in MW")

    # Dates
    effective_date: Optional[str] = Field(None, description="Contract effective date")
    commercial_operation_date: Optional[str] = Field(None, description="Expected COD")
    delivery_term_start: Optional[str] = Field(None, description="Delivery term start date")
    delivery_term_years: Optional[int] = Field(None, description="Delivery term in years")
    contract_end_date: Optional[str] = Field(None, description="Contract end date")

    # Pricing
    energy_price: Optional[str] = Field(None, description="Energy price ($/MWh or structure)")
    price_escalation: Optional[str] = Field(None, description="Annual price escalation")
    capacity_payment: Optional[str] = Field(None, description="Capacity payment if any")

    # Delivery Terms
    delivery_point: Optional[str] = Field(None, description="Point of delivery")
    delivery_obligations: Optional[str] = Field(None, description="Delivery obligations")
    annual_contract_quantity: Optional[float] = Field(None, description="Annual contract quantity (MWh)")

    # RECs and Environmental Attributes
    rec_transfer: Optional[bool] = Field(None, description="Are RECs transferred to buyer")
    environmental_attributes: Optional[str] = Field(None, description="Environmental attributes handling")

    # Performance and Guarantees
    guaranteed_capacity_factor: Optional[float] = Field(None, description="Guaranteed capacity factor")
    performance_requirements: Optional[str] = Field(None, description="Performance requirements")
    liquidated_damages: Optional[str] = Field(None, description="Liquidated damages provisions")

    # Curtailment
    curtailment_provisions: Optional[str] = Field(None, description="Curtailment terms")
    curtailment_compensation: Optional[str] = Field(None, description="Curtailment compensation")

    # Credit Support
    seller_collateral: Optional[str] = Field(None, description="Seller collateral requirements")
    buyer_collateral: Optional[str] = Field(None, description="Buyer collateral requirements")

    # Termination
    termination_provisions: Optional[str] = Field(None, description="Termination provisions")
    early_termination_fee: Optional[str] = Field(None, description="Early termination fees")

    # Other Important Terms
    force_majeure: Optional[str] = Field(None, description="Force majeure provisions")
    change_in_law: Optional[str] = Field(None, description="Change in law provisions")
    dispatch_rights: Optional[str] = Field(None, description="Dispatch and scheduling rights")

    # Red Flags
    red_flags: List[str] = Field(default_factory=list, description="Identified red flags")
    key_risks: List[str] = Field(default_factory=list, description="Key commercial risks")


class PPAExtractor:
    """Extractor for Power Purchase Agreements"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.0,  # Use 0 for extraction
            api_key=settings.OPENAI_API_KEY
        )

        self.extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert in renewable energy Power Purchase Agreements.
            Extract key terms and provisions from the PPA text provided.

            Focus on:
            1. Parties and project details
            2. Contract dates and term
            3. Pricing structure and escalation
            4. Delivery obligations and points
            5. REC and environmental attribute transfer
            6. Performance guarantees and damages
            7. Curtailment provisions
            8. Credit support requirements
            9. Termination provisions
            10. Key risks and red flags

            For numerical values, extract exact numbers.
            For dates, use format: YYYY-MM-DD or "Not specified"
            For boolean fields, use true/false or null if unclear.

            Identify RED FLAGS such as:
            - Unfavorable pricing terms
            - Short contract duration (<10 years)
            - Excessive liquidated damages
            - Unclear delivery obligations
            - Unfavorable curtailment terms
            - Excessive collateral requirements
            - Broad termination rights for buyer
            """),
            ("user", "PPA Text:\n\n{text}\n\nExtract the key terms in JSON format.")
        ])

    def extract_with_regex(self, text: str) -> Dict[str, Any]:
        """
        Extract terms using regex patterns

        Args:
            text: PPA text

        Returns:
            Dictionary of extracted terms
        """
        terms = {}

        # Extract pricing ($/MWh patterns)
        price_pattern = r'\$(\d+\.?\d*)\s*(?:per|/)\s*MWh'
        price_matches = re.findall(price_pattern, text, re.IGNORECASE)
        if price_matches:
            terms['energy_price'] = f"${price_matches[0]}/MWh"

        # Extract capacity (MW)
        capacity_pattern = r'(\d+\.?\d*)\s*(?:MW|megawatt)'
        capacity_matches = re.findall(capacity_pattern, text, re.IGNORECASE)
        if capacity_matches:
            # Take the most common value
            terms['contract_capacity_mw'] = float(capacity_matches[0])

        # Extract term duration (years)
        term_pattern = r'(?:term of|period of|duration of)\s*(\d+)\s*years?'
        term_matches = re.findall(term_pattern, text, re.IGNORECASE)
        if term_matches:
            terms['delivery_term_years'] = int(term_matches[0])

        # Extract dates (various formats)
        date_patterns = [
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}'
        ]

        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))

        if dates:
            terms['extracted_dates'] = dates[:5]  # Keep first 5 dates found

        # Extract escalation rates
        escalation_pattern = r'(\d+\.?\d*)\s*%\s*(?:per year|annual|annually)'
        escalation_matches = re.findall(escalation_pattern, text, re.IGNORECASE)
        if escalation_matches:
            terms['price_escalation'] = f"{escalation_matches[0]}% per year"

        # Check for REC transfer
        if re.search(r'renewable energy credit|(?:^|\s)REC(?:s|\s)', text, re.IGNORECASE):
            if re.search(r'transfer.*REC|REC.*transfer|buyer.*entitled.*REC', text, re.IGNORECASE):
                terms['rec_transfer'] = True

        # Identify parties
        seller_pattern = r'(?:Seller|Generator|Developer):\s*([A-Z][A-Za-z\s&,\.]+(?:LLC|Inc|Corp|Company))'
        buyer_pattern = r'(?:Buyer|Offtaker|Purchaser):\s*([A-Z][A-Za-z\s&,\.]+(?:LLC|Inc|Corp|Company))'

        seller_match = re.search(seller_pattern, text)
        buyer_match = re.search(buyer_pattern, text)

        if seller_match:
            terms['seller'] = seller_match.group(1).strip()
        if buyer_match:
            terms['buyer'] = buyer_match.group(1).strip()

        return terms

    async def extract_with_llm(self, text: str, max_length: int = 15000) -> Dict[str, Any]:
        """
        Extract terms using LLM

        Args:
            text: PPA text
            max_length: Maximum text length to send to LLM

        Returns:
            Dictionary of extracted terms
        """
        try:
            # Truncate if too long
            text_to_process = text[:max_length] if len(text) > max_length else text

            # Create prompt
            messages = self.extraction_prompt.format_messages(text=text_to_process)

            # Get response
            response = await self.llm.ainvoke(messages)

            # Parse JSON response
            import json
            try:
                extracted_data = json.loads(response.content)
                logger.info("LLM extraction successful")
                return extracted_data
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM response as JSON")
                return {"raw_response": response.content}

        except Exception as e:
            logger.error(f"LLM extraction failed: {str(e)}")
            return {}

    def identify_red_flags(self, terms: Dict[str, Any]) -> List[str]:
        """
        Identify red flags in PPA terms

        Args:
            terms: Extracted PPA terms

        Returns:
            List of red flags
        """
        red_flags = []

        # Check contract duration
        if terms.get('delivery_term_years'):
            if terms['delivery_term_years'] < 10:
                red_flags.append(
                    f"Short contract term ({terms['delivery_term_years']} years) - "
                    "may impact project financing"
                )

        # Check pricing
        if terms.get('energy_price'):
            price_str = terms['energy_price']
            # Extract numeric price
            price_match = re.search(r'\$?(\d+\.?\d*)', price_str)
            if price_match:
                price = float(price_match.group(1))
                if price < 20:
                    red_flags.append(
                        f"Low energy price (${price}/MWh) - verify market conditions"
                    )

        # Check REC transfer
        if terms.get('rec_transfer') is False:
            red_flags.append("RECs not transferred to buyer - impacts project economics")

        # Check for missing key terms
        critical_terms = [
            'seller', 'buyer', 'energy_price', 'delivery_term_years',
            'commercial_operation_date', 'delivery_point'
        ]

        missing_terms = [term for term in critical_terms if not terms.get(term)]
        if missing_terms:
            red_flags.append(f"Missing critical terms: {', '.join(missing_terms)}")

        return red_flags

    async def extract(self, text: str, use_llm: bool = True) -> PPATerms:
        """
        Extract PPA terms using hybrid approach

        Args:
            text: PPA text content
            use_llm: Whether to use LLM extraction

        Returns:
            PPATerms object with extracted data
        """
        # Start with regex extraction
        regex_terms = self.extract_with_regex(text)
        logger.info(f"Regex extraction found {len(regex_terms)} terms")

        # Enhance with LLM if available
        if use_llm and settings.OPENAI_API_KEY:
            llm_terms = await self.extract_with_llm(text)
            # Merge results (LLM takes precedence for conflicts)
            combined_terms = {**regex_terms, **llm_terms}
        else:
            combined_terms = regex_terms

        # Identify red flags
        red_flags = self.identify_red_flags(combined_terms)
        combined_terms['red_flags'] = red_flags

        # Create PPATerms object
        try:
            ppa_terms = PPATerms(**combined_terms)
            logger.info("PPA extraction completed successfully")
            return ppa_terms
        except Exception as e:
            logger.error(f"Failed to create PPATerms object: {str(e)}")
            # Return partial data
            ppa_terms = PPATerms()
            for key, value in combined_terms.items():
                if hasattr(ppa_terms, key):
                    setattr(ppa_terms, key, value)
            return ppa_terms

    def calculate_ppa_metrics(self, terms: PPATerms) -> Dict[str, Any]:
        """
        Calculate key PPA metrics

        Args:
            terms: Extracted PPA terms

        Returns:
            Dictionary of calculated metrics
        """
        metrics = {}

        # Calculate lifetime contract value (if possible)
        if all([
            terms.contract_capacity_mw,
            terms.delivery_term_years,
            terms.energy_price
        ]):
            # Extract numeric price
            price_match = re.search(r'\$?(\d+\.?\d*)', terms.energy_price)
            if price_match:
                price = float(price_match.group(1))

                # Assume capacity factor (use conservative estimate)
                capacity_factor = 0.30  # 30% default

                # Calculate annual energy (MWh)
                annual_energy = terms.contract_capacity_mw * 8760 * capacity_factor

                # Calculate annual revenue
                annual_revenue = annual_energy * price

                # Calculate lifetime value (without escalation for simplicity)
                lifetime_value = annual_revenue * terms.delivery_term_years

                metrics['estimated_annual_energy_mwh'] = round(annual_energy, 0)
                metrics['estimated_annual_revenue_usd'] = round(annual_revenue, 0)
                metrics['estimated_lifetime_revenue_usd'] = round(lifetime_value, 0)

        return metrics


# Global PPA extractor instance
ppa_extractor = PPAExtractor()

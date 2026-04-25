"""Design analyzer service for extracting design specifications."""
import logging
import json
from typing import Optional

from models import DesignSpecification, UnslothProvider
from instructions import get_design_analyzer_prompt

logger = logging.getLogger(__name__)


class DesignAnalyzerService:
    """Service for analyzing conversations and extracting design specifications."""

    def __init__(self, llm_provider: UnslothProvider):
        self.llm_provider = llm_provider

    async def analyze_conversation(
        self, conversation_text: str, max_tokens: int = 1024
    ) -> DesignSpecification:
        """Analyze conversation and extract design specifications."""
        try:
            prompt = get_design_analyzer_prompt(conversation_text)
            analysis = await self.llm_provider.generate(prompt, max_tokens)

            logger.info("Design analysis completed")

            # Parse analysis into DesignSpecification
            spec = self._parse_analysis(analysis)
            return spec
        except Exception as e:
            logger.error(f"Error analyzing design: {e}")
            # Return default/empty specification on error
            return DesignSpecification(
                description="Unable to analyze design from conversation"
            )

    def _parse_analysis(self, analysis_text: str) -> DesignSpecification:
        """Parse LLM analysis output into DesignSpecification."""
        # Try to extract JSON from response
        try:
            # Look for JSON in response
            start_idx = analysis_text.find("{")
            end_idx = analysis_text.rfind("}") + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = analysis_text[start_idx:end_idx]
                data = json.loads(json_str)

                return DesignSpecification(
                    description=data.get("description", ""),
                    dimensions=data.get("dimensions"),
                    material=data.get("material"),
                    color=data.get("color"),
                    fabrication_method=data.get("fabrication_method"),
                    additional_notes=data.get("additional_notes"),
                )
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Could not parse JSON from analysis: {e}")

        # Fallback: create specification from text
        return DesignSpecification(
            description=analysis_text[:500],  # Use first 500 chars as description
            material="To be determined",
            fabrication_method="To be determined",
        )

    async def extract_dimensions(
        self, design_description: str
    ) -> Optional[dict]:
        """Extract dimensional information from design description."""
        # Simple regex-based extraction (in production, could use LLM)
        import re

        # Pattern for dimensions like "100mm", "10 x 20 x 30", etc.
        dimension_pattern = r"(\d+\.?\d*)\s*(mm|cm|inch|in|m)"
        matches = re.findall(dimension_pattern, design_description, re.IGNORECASE)

        if matches:
            return {
                "values": matches,
                "raw": design_description,
            }
        return None

    async def extract_materials(
        self, design_description: str
    ) -> Optional[list]:
        """Extract material suggestions from design description."""
        materials = [
            "PLA",
            "ABS",
            "PETG",
            "Nylon",
            "TPU",
            "Resin",
            "Wood",
            "Metal",
            "Plastic",
            "Aluminum",
            "Steel",
            "Brass",
            "Copper",
        ]

        found_materials = []
        for material in materials:
            if material.lower() in design_description.lower():
                found_materials.append(material)

        return found_materials if found_materials else None

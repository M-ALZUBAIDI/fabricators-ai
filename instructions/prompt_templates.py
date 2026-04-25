"""Prompt templates for different use cases."""
from enum import Enum
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class InstructionType(str, Enum):
    """Types of instructions/prompts."""

    FABRICATION_ASSISTANT = "fabrication_assistant"
    REPORT_GENERATOR = "report_generator"
    DESIGN_ANALYZER = "design_analyzer"


class PromptTemplate:
    """Load and manage prompt templates."""

    TEMPLATES_DIR = "instructions"

    @staticmethod
    def load(instruction_type: InstructionType) -> str:
        """Load prompt template from file."""
        try:
            # Map instruction types to filenames
            filename_map = {
                InstructionType.FABRICATION_ASSISTANT: "fabrication_assistant.md",
                InstructionType.REPORT_GENERATOR: "report_generator.md",
                InstructionType.DESIGN_ANALYZER: "design_analyzer.md",
            }

            filename = filename_map.get(instruction_type)
            if not filename:
                raise ValueError(f"Unknown instruction type: {instruction_type}")

            filepath = f"{PromptTemplate.TEMPLATES_DIR}/{filename}"

            with open(filepath, "r") as f:
                template = f.read()

            logger.info(f"Loaded prompt template: {filename}")
            return template
        except FileNotFoundError:
            logger.error(f"Prompt template not found: {filepath}")
            raise
        except Exception as e:
            logger.error(f"Error loading prompt template: {e}")
            raise

    @staticmethod
    def inject_variables(template: str, variables: Dict[str, str]) -> str:
        """Inject variables into template."""
        result = template
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        return result


def get_fabrication_assistant_prompt(user_question: str) -> str:
    """Get fabrication assistant prompt with user question."""
    template = PromptTemplate.load(InstructionType.FABRICATION_ASSISTANT)
    variables = {"user_question": user_question}
    return PromptTemplate.inject_variables(template, variables)


def get_report_generator_prompt(
    conversation_summary: str, design_details: str
) -> str:
    """Get report generator prompt."""
    template = PromptTemplate.load(InstructionType.REPORT_GENERATOR)
    variables = {
        "conversation_summary": conversation_summary,
        "design_details": design_details,
    }
    return PromptTemplate.inject_variables(template, variables)


def get_design_analyzer_prompt(conversation_text: str) -> str:
    """Get design analyzer prompt."""
    template = PromptTemplate.load(InstructionType.DESIGN_ANALYZER)
    variables = {"conversation": conversation_text}
    return PromptTemplate.inject_variables(template, variables)

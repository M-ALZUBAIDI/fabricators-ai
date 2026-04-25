"""Report generation service."""
import logging
import json
import base64
from datetime import datetime

from models import ReportData, DesignSpecification, Design3DAsset
from models.llm_provider import LLMProvider
from instructions import get_report_generator_prompt
from services.design_analyzer import DesignAnalyzerService
from services.chat_service import ChatService

logger = logging.getLogger(__name__)


class ReportService:
    """Service for generating reports with embedded 3D assets."""

    def __init__(
        self,
        llm_provider: LLMProvider,
        chat_service: ChatService,
        design_analyzer: DesignAnalyzerService,
    ):
        self.llm_provider = llm_provider
        self.chat_service = chat_service
        self.design_analyzer = design_analyzer
        self.reports = {}  # In-memory storage (production: use database)

    async def generate_report(
        self, session_id: str, assets_3d: list = None, max_tokens: int = 2048
    ) -> ReportData:
        """Generate a report from conversation."""
        if assets_3d is None:
            assets_3d = []

        try:
            # Get conversation data
            history = await self.chat_service.get_conversation_history(session_id)
            if not history:
                raise ValueError(f"No conversation found for session {session_id}")

            # Build conversation text
            conversation_text = self._build_conversation_text(history.messages)
            conversation_summary = await self.chat_service.get_conversation_summary(
                session_id
            )

            # Analyze design from conversation
            design_spec = await self.design_analyzer.analyze_conversation(
                conversation_text, max_tokens // 2
            )

            # Generate report content using LLM
            report_prompt = get_report_generator_prompt(
                conversation_summary, design_spec.description
            )
            report_content = await self.llm_provider.generate(
                report_prompt, max_tokens // 2
            )

            # Extract key points from report
            key_points = self._extract_key_points(report_content)

            # Create report data
            report = ReportData(
                session_id=session_id,
                conversation_summary=conversation_summary,
                design_specification=design_spec,
                key_points=key_points,
                assets_3d=assets_3d,  # Embed 3D assets
                conversation_length=len(history.messages),
            )

            # Store report
            self.reports[report.report_id] = report

            logger.info(f"Generated report: {report.report_id}")
            return report

        except Exception as e:
            logger.error(f"Error generating report for {session_id}: {e}")
            raise

    def _build_conversation_text(self, messages) -> str:
        """Build a text representation of conversation messages."""
        conversation_parts = []
        for msg in messages:
            role_prefix = "User:" if msg.role == "user" else "Assistant:"
            conversation_parts.append(f"{role_prefix} {msg.content}")

        return "\n".join(conversation_parts)

    def _extract_key_points(self, text: str, max_points: int = 5) -> list[str]:
        """Extract key points from text."""
        # Simple implementation: split by sentences and take first N
        sentences = text.split(".")
        key_points = [
            s.strip()
            for s in sentences[:max_points]
            if len(s.strip()) > 10
        ]
        return key_points

    async def export_report_to_json(self, report_id: str) -> dict:
        """Export report as JSON."""
        report = self.reports.get(report_id)
        if not report:
            raise ValueError(f"Report not found: {report_id}")

        # Convert to dict (Pydantic model_dump)
        report_dict = report.model_dump(mode="python")

        logger.info(f"Exported report to JSON: {report_id}")
        return report_dict

    async def export_report_to_pdf(self, report_id: str) -> bytes:
        """Export report as PDF."""
        report = self.reports.get(report_id)
        if not report:
            raise ValueError(f"Report not found: {report_id}")

        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import (
                SimpleDocTemplate,
                Paragraph,
                Spacer,
                Table,
                TableStyle,
                PageBreak,
            )
            from reportlab.lib import colors

            # Create PDF
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(
                pdf_buffer, pagesize=letter, title="Fabrication Report"
            )

            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#1f4788"),
                spaceAfter=30,
            )
            heading_style = ParagraphStyle(
                "CustomHeading",
                parent=styles["Heading2"],
                fontSize=14,
                textColor=colors.HexColor("#333333"),
                spaceAfter=12,
                spaceBefore=12,
            )

            # Build content
            content = []

            # Title
            content.append(
                Paragraph("Fabrication Report", title_style)
            )
            content.append(
                Paragraph(f"Report ID: {report.report_id}", styles["Normal"])
            )
            content.append(
                Paragraph(
                    f"Generated: {report.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
                    styles["Normal"],
                )
            )
            content.append(Spacer(1, 0.3 * inch))

            # Summary
            content.append(Paragraph("Summary", heading_style))
            content.append(Paragraph(report.conversation_summary, styles["Normal"]))
            content.append(Spacer(1, 0.2 * inch))

            # Design Specification
            content.append(Paragraph("Design Specification", heading_style))
            spec_data = [
                ["Aspect", "Details"],
                ["Description", report.design_specification.description or "N/A"],
                ["Material", report.design_specification.material or "N/A"],
                ["Fabrication Method", report.design_specification.fabrication_method or "N/A"],
                ["Color/Finish", report.design_specification.color or "N/A"],
            ]
            spec_table = Table(spec_data, colWidths=[2 * inch, 4 * inch])
            spec_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4788")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ])
            )
            content.append(spec_table)
            content.append(Spacer(1, 0.3 * inch))

            # Key Points
            if report.key_points:
                content.append(Paragraph("Key Points", heading_style))
                for point in report.key_points:
                    content.append(
                        Paragraph(f"• {point}", styles["Normal"])
                    )
                content.append(Spacer(1, 0.2 * inch))

            # 3D Assets Info
            if report.assets_3d:
                content.append(Paragraph("3D Assets", heading_style))
                for asset in report.assets_3d:
                    content.append(
                        Paragraph(
                            f"• {asset.filename} ({asset.format.upper()}) - {asset.size_bytes} bytes",
                            styles["Normal"],
                        )
                    )

            # Build PDF
            doc.build(content)
            pdf_buffer.seek(0)

            logger.info(f"Generated PDF for report: {report_id}")
            return pdf_buffer.getvalue()

        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            raise

    def get_report(self, report_id: str) -> ReportData:
        """Retrieve a stored report."""
        return self.reports.get(report_id)

    def get_report_by_share_token(self, share_token: str) -> ReportData:
        """Retrieve report by share token."""
        for report in self.reports.values():
            if report.share_token == share_token:
                return report
        return None


# Import BytesIO for PDF generation
from io import BytesIO

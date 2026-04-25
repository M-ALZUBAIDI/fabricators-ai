"""Tests for report service."""
import pytest


@pytest.mark.asyncio
async def test_generate_report(report_service, chat_service):
    """Test generating a report."""
    # Setup
    session_id = await chat_service.start_conversation()
    await chat_service.send_message(session_id, "I need to make a 100mm cube")
    await chat_service.send_message(
        session_id, "What material should I use for 3D printing?"
    )

    # Generate report
    report = await report_service.generate_report(session_id)

    assert report is not None
    assert report.report_id is not None
    assert report.session_id == session_id
    assert len(report.conversation_summary) > 0
    assert report.design_specification is not None
    assert len(report.key_points) > 0


@pytest.mark.asyncio
async def test_export_report_to_json(report_service, chat_service):
    """Test exporting report to JSON."""
    # Setup
    session_id = await chat_service.start_conversation()
    await chat_service.send_message(session_id, "How do I design something?")

    # Generate report
    report = await report_service.generate_report(session_id)

    # Export
    report_json = await report_service.export_report_to_json(report.report_id)

    assert report_json is not None
    assert report_json["report_id"] == report.report_id
    assert "conversation_summary" in report_json
    assert "design_specification" in report_json


@pytest.mark.asyncio
async def test_get_report(report_service, chat_service):
    """Test retrieving a stored report."""
    # Setup
    session_id = await chat_service.start_conversation()
    await chat_service.send_message(session_id, "Test question")

    # Generate and retrieve
    report = await report_service.generate_report(session_id)
    retrieved = report_service.get_report(report.report_id)

    assert retrieved is not None
    assert retrieved.report_id == report.report_id

"""Tests for chat service."""
import pytest


@pytest.mark.asyncio
async def test_start_conversation(chat_service):
    """Test starting a conversation."""
    session_id = await chat_service.start_conversation()
    assert session_id is not None
    assert len(session_id) > 0


@pytest.mark.asyncio
async def test_send_message(chat_service):
    """Test sending a message."""
    session_id = await chat_service.start_conversation()
    response = await chat_service.send_message(session_id, "How do I make a cube?")

    assert response.session_id == session_id
    assert len(response.answer) > 0
    assert response.model_used is not None


@pytest.mark.asyncio
async def test_get_conversation_history(chat_service):
    """Test getting conversation history."""
    session_id = await chat_service.start_conversation()
    await chat_service.send_message(session_id, "Question 1")
    await chat_service.send_message(session_id, "Question 2")

    history = await chat_service.get_conversation_history(session_id)
    assert history is not None
    assert len(history.messages) == 4  # 2 user + 2 assistant


@pytest.mark.asyncio
async def test_get_conversation_summary(chat_service):
    """Test getting conversation summary."""
    session_id = await chat_service.start_conversation()
    await chat_service.send_message(session_id, "How do I 3D print?")

    summary = await chat_service.get_conversation_summary(session_id)
    assert summary is not None
    assert "How do I 3D print?" in summary

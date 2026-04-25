"""Chat service for handling conversations."""
import logging
from typing import List, Optional
from datetime import datetime
import uuid

from models import ChatMessage, ConversationHistory, ChatResponse
from models.llm_provider import LLMProvider
from instructions import get_fabrication_assistant_prompt

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing chat conversations."""

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        # In-memory storage (in production, use database)
        self.conversations: dict[str, ConversationHistory] = {}

    async def start_conversation(self, session_id: Optional[str] = None) -> str:
        """Start a new conversation."""
        if session_id is None:
            session_id = str(uuid.uuid4())

        self.conversations[session_id] = ConversationHistory(session_id=session_id)
        logger.info(f"Started conversation: {session_id}")
        return session_id

    async def send_message(
        self, session_id: str, user_message: str, max_tokens: int = 1024
    ) -> ChatResponse:
        """Send a message and get response."""
        if session_id not in self.conversations:
            await self.start_conversation(session_id)

        conversation = self.conversations[session_id]

        # Add user message to history
        user_msg = ChatMessage(role="user", content=user_message)
        conversation.messages.append(user_msg)
        logger.info(f"User message added to {session_id}: {user_message[:50]}...")

        # Generate response using LLM
        try:
            prompt = get_fabrication_assistant_prompt(user_message)
            response_text = await self.llm_provider.generate(prompt, max_tokens)

            # Add assistant message to history
            assistant_msg = ChatMessage(role="assistant", content=response_text)
            conversation.messages.append(assistant_msg)
            conversation.updated_at = datetime.utcnow()

            logger.info(f"Generated response for {session_id}")

            return ChatResponse(
                session_id=session_id,
                answer=response_text,
                model_used="unsloth/mock",
            )
        except Exception as e:
            logger.error(f"Error generating response for {session_id}: {e}")
            raise

    async def get_conversation_history(
        self, session_id: str
    ) -> Optional[ConversationHistory]:
        """Get full conversation history."""
        return self.conversations.get(session_id)

    async def get_conversation_messages(self, session_id: str) -> List[ChatMessage]:
        """Get conversation messages only."""
        conversation = self.conversations.get(session_id)
        if conversation:
            return conversation.messages
        return []

    async def get_conversation_summary(self, session_id: str) -> str:
        """Generate a summary of the conversation."""
        messages = await self.get_conversation_messages(session_id)

        # Create summary from messages
        summary_parts = []
        for i, msg in enumerate(messages):
            if msg.role == "user":
                summary_parts.append(f"Q: {msg.content[:100]}")
            else:
                summary_parts.append(f"A: {msg.content[:100]}")

        return "\n".join(summary_parts)

    def clear_conversation(self, session_id: str) -> None:
        """Clear a conversation."""
        if session_id in self.conversations:
            del self.conversations[session_id]
            logger.info(f"Cleared conversation: {session_id}")

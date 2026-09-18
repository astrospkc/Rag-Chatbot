from typing import Dict, List
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# In-memory store for guest / non-employee chat sessions: session_id -> history
_guest_session_store: Dict[str, InMemoryChatMessageHistory] = {}


def get_guest_chat_history(session_id: str) -> InMemoryChatMessageHistory:
    """
    Retrieve or create an ephemeral in-memory chat history for a non-employee session.
    """
    if session_id not in _guest_session_store:
        _guest_session_store[session_id] = InMemoryChatMessageHistory()
    return _guest_session_store[session_id]


def add_guest_chat_turn(session_id: str, user_query: str, ai_response: str) -> None:
    """
    Append a user question and AI answer to the guest's session history.
    """
    history = get_guest_chat_history(session_id)
    history.add_user_message(user_query)
    history.add_ai_message(ai_response)


def format_messages_to_string(messages: List[BaseMessage], max_messages: int = 6) -> str:
    """
    Format the most recent messages into a readable conversation string for LLM prompts.
    """
    recent_messages = messages[-max_messages:]
    formatted_lines = []
    for msg in recent_messages:
        if isinstance(msg, HumanMessage):
            formatted_lines.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage):
            formatted_lines.append(f"Assistant: {msg.content}")
        else:
            formatted_lines.append(f"{msg.type.capitalize()}: {msg.content}")
    return "\n".join(formatted_lines)


def get_formatted_guest_history(session_id: str, max_messages: int = 6) -> str:
    """
    Convenience helper to fetch and format a guest's recent chat history.
    """
    history = get_guest_chat_history(session_id)
    print(f"Formatting chat history for session {session_id}: {[msg.content for msg in history.messages]}")
    return format_messages_to_string(history.messages, max_messages=max_messages)


def clear_guest_history(session_id: str) -> None:
    """
    Clear/reset a guest's session history.
    """
    if session_id in _guest_session_store:
        _guest_session_store[session_id].clear()


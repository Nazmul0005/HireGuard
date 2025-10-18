"""
Memory management for the chatbot application.
"""

from typing import Dict, List
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory

# Global memory store for user sessions
memories: Dict[str, ChatMessageHistory] = {}

def get_memory(user_id: str) -> ChatMessageHistory:
    """
    Get or create memory for a user session.
    
    Args:
        user_id (str): The user identifier
        
    Returns:
        ChatMessageHistory: The message history instance for the user
    """
    if user_id not in memories:
        memories[user_id] = ChatMessageHistory()
    return memories[user_id]

def format_chat_history(memory: ChatMessageHistory) -> str:
    """
    Format chat history from memory for use in prompts.
    
    Args:
        memory (ChatMessageHistory): The message history instance
        
    Returns:
        str: Formatted chat history
    """
    try:
        messages = memory.messages
        
        if not messages:
            return "No previous conversation."
        
        formatted_history = []
        for message in messages:
            if isinstance(message, HumanMessage):
                formatted_history.append(f"User: {message.content}")
            elif isinstance(message, AIMessage):
                formatted_history.append(f"AI: {message.content}")
            else:
                # Fallback for other message types
                formatted_history.append(f"{message.__class__.__name__}: {message.content}")
        
        return "\n".join(formatted_history)
    except Exception as e:
        print(f"Error formatting chat history: {e}")
        return "No previous conversation."

def save_conversation(user_id: str, human_message: str, ai_message: str) -> None:
    """
    Save a conversation turn to memory.
    
    Args:
        user_id (str): The user identifier
        human_message (str): The human message
        ai_message (str): The AI response
    """
    try:
        memory = get_memory(user_id)
        memory.add_user_message(human_message)
        memory.add_ai_message(ai_message)
    except Exception as e:
        print(f"Error saving conversation: {e}")
from pydantic import BaseModel, Field
from typing import List, Optional, Annotated

class ChatRequest(BaseModel):
    query : Annotated[str, Field(description="The user's query to the chat model.")]
    user_id: Annotated[Optional[str], Field(description="Optional user identifier for session management.")] = None


class ChatResponse(BaseModel):
    response: Annotated[str, Field(description="The chat model's response to the user's query.")]
    category: Annotated[str, Field(description="List of categories relevant to the response.")] = []

class StreamingChatResponse(BaseModel):
    """Schema for streaming chat response events"""
    token: Annotated[Optional[str], Field(description="A token/chunk of the response text")] = None
    category: Annotated[Optional[str], Field(description="The classified category of the query")] = None
    type: Annotated[str, Field(description="Type of event: 'content', 'category', 'done', or 'error'")]
    error: Annotated[Optional[str], Field(description="Error message if type is 'error'")] = None
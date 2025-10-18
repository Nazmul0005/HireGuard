

"""
FastAPI chatbot backend with intent classification and multiple response modes.
"""

import os
from typing import Dict
from fastapi import FastAPI, Body, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from .chains import classifier_chain, get_rag_chain, gen_chain, conv_chain, stream_rag_response, stream_generation_response, stream_conversation_response
from .vectorstore import is_vectorstore_ready
from .memory import get_memory, format_chat_history, save_conversation
from .schema import ChatRequest, ChatResponse
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["Chatbot"],
)

@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    """
    Main chat endpoint that handles user queries with intent classification.
    
    Args:
        body (Dict): JSON body containing 'query' and optional 'user_id'
        
    Returns:
        Dict: Response containing the chatbot's reply or error message
    """
    try:
        # Extract query and user_id from request body
        query = body.query
        user_id = body.user_id
        
        # Validate query
        if not query or not query.strip():
            return {"error": "Query is required and cannot be empty"}
        
        # Get or create memory for user
        memory = get_memory(user_id)
        
        # Get formatted chat history
        chat_history = format_chat_history(memory)
        
        # Classify the query intent
        try:
            category = classifier_chain.invoke({"query": query}).strip().lower()
            print(f"Classified query as: {category}")
        except Exception as e:
            print(f"Error in intent classification: {e}")
            category = "general_chat"  # Default fallback
        
        # Route to appropriate chain based on classification
        response = ""
        
        if category == "system_info":
            # Check if vectorstore is ready for RAG
            if not is_vectorstore_ready():
                return ChatResponse(
                    response="I'm still loading my knowledge base. Please try again in a few seconds.",
                    category=category
                )
            
            # Use RAG chain for system/app questions
            try:
                rag_chain = get_rag_chain()
                if rag_chain is None:
                    return ChatResponse(
                        response="My knowledge base is still loading. Please try again shortly.",
                        category=category
                    )
                
                result = rag_chain.invoke({
                    "question": query,
                    "chat_history": memory.messages
                })
                response = result["answer"]
            except Exception as e:
                print(f"Error in RAG chain: {e}")
                response = "I'm sorry, I encountered an error while searching for information. Please try again."
                
        elif category == "content_generation":
            # Use generation chain for content creation
            try:
                response = gen_chain.invoke({"query": query, "chat_history": chat_history})
            except Exception as e:
                print(f"Error in generation chain: {e}")
                response = "I'm sorry, I encountered an error while generating content. Please try again."
                
        else:
            # Use conversation chain for general chat
            try:
                response = conv_chain.invoke({"query": query, "chat_history": chat_history})
            except Exception as e:
                print(f"Error in conversation chain: {e}")
                response = "I'm sorry, I encountered an error while processing your message. Please try again."
        
        # Save interaction to memory
        try:
            save_conversation(user_id, query, response)
        except Exception as e:
            print(f"Error saving to memory: {e}")
            # Continue even if memory save fails
        
        return ChatResponse(response=response, category=category)
        
    except Exception as e:
        print(f"Unexpected error in chat endpoint: {e}")
        return {"error": f"An unexpected error occurred: {str(e)}"}

@router.post("/chat/stream")
async def chat_stream(body: ChatRequest):
    """
    Streaming chat endpoint that handles user queries with Server-Sent Events.
    
    Args:
        body (ChatRequest): JSON body containing 'query' and optional 'user_id'
        
    Returns:
        StreamingResponse: Server-sent events stream with chatbot responses
    """
    async def generate_response():
        try:
            # Extract query and user_id from request body
            query = body.query
            user_id = body.user_id
            
            # Validate query
            if not query or not query.strip():
                yield f"data: {json.dumps({'error': 'Query is required and cannot be empty', 'type': 'error'})}\n\n"
                return
            
            # Get or create memory for user
            memory = get_memory(user_id)
            
            # Get formatted chat history
            chat_history = format_chat_history(memory)
            
            # Classify the query intent
            try:
                category = classifier_chain.invoke({"query": query}).strip().lower()
                print(f"Classified query as: {category}")
                
                # Send category information
                yield f"data: {json.dumps({'category': category, 'type': 'category'})}\n\n"
                
            except Exception as e:
                print(f"Error in intent classification: {e}")
                category = "general_chat"  # Default fallback
                yield f"data: {json.dumps({'category': category, 'type': 'category'})}\n\n"
            
            # Accumulate response for memory saving
            full_response = ""
            
            # Route to appropriate streaming chain based on classification
            if category == "system_info":
                # Check if vectorstore is ready for RAG
                if not is_vectorstore_ready():
                    error_msg = "I'm still loading my knowledge base. Please try again in a few seconds."
                    yield f"data: {json.dumps({'token': error_msg, 'type': 'content'})}\n\n"
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    return
                
                # Stream RAG response
                try:
                    async for token in stream_rag_response(query, memory.messages):
                        full_response += token
                        yield f"data: {json.dumps({'token': token, 'type': 'content'})}\n\n"
                except Exception as e:
                    print(f"Error in RAG streaming: {e}")
                    error_msg = "I'm sorry, I encountered an error while searching for information. Please try again."
                    yield f"data: {json.dumps({'token': error_msg, 'type': 'content'})}\n\n"
                    full_response = error_msg
                    
            elif category == "content_generation":
                # Stream generation response
                try:
                    async for token in stream_generation_response(query, chat_history):
                        full_response += token
                        yield f"data: {json.dumps({'token': token, 'type': 'content'})}\n\n"
                except Exception as e:
                    print(f"Error in generation streaming: {e}")
                    error_msg = "I'm sorry, I encountered an error while generating content. Please try again."
                    yield f"data: {json.dumps({'token': error_msg, 'type': 'content'})}\n\n"
                    full_response = error_msg
                    
            else:
                # Stream conversation response
                try:
                    async for token in stream_conversation_response(query, chat_history):
                        full_response += token
                        yield f"data: {json.dumps({'token': token, 'type': 'content'})}\n\n"
                except Exception as e:
                    print(f"Error in conversation streaming: {e}")
                    error_msg = "I'm sorry, I encountered an error while processing your message. Please try again."
                    yield f"data: {json.dumps({'token': error_msg, 'type': 'content'})}\n\n"
                    full_response = error_msg
            
            # Save interaction to memory
            try:
                save_conversation(user_id, query, full_response)
            except Exception as e:
                print(f"Error saving to memory: {e}")
                # Continue even if memory save fails
            
            # Send completion signal
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            print(f"Unexpected error in streaming chat endpoint: {e}")
            yield f"data: {json.dumps({'error': f'An unexpected error occurred: {str(e)}', 'type': 'error'})}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

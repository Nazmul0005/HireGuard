"""
LangChain chains for the chatbot application.
"""
from langchain.chains import ConversationalRetrievalChain
from langchain_core.output_parsers import StrOutputParser
from .prompts import classifier_prompt, gen_prompt, conv_prompt
from .vectorstore import get_vectorstore, is_vectorstore_ready
from langchain_openai import ChatOpenAI
from com.mhire.app.config.config import Config

config = Config()
model_name = config.model_name2
SEARCH_K = 2

llm = ChatOpenAI(model=model_name, temperature=0.5)
llm_classifier = ChatOpenAI(model="gpt-5", temperature=0.5)

# Create streaming-enabled LLM instances
streaming_llm = ChatOpenAI(model="gpt-4o", temperature=0.5, streaming=True)

# Create classifier chain using new syntax
classifier_chain = classifier_prompt | llm_classifier | StrOutputParser()

# Create content generation chain using new syntax
gen_chain = gen_prompt | llm | StrOutputParser()

# Create general conversation chain using new syntax
conv_chain = conv_prompt | llm | StrOutputParser()

# Create streaming chains
streaming_gen_chain = gen_prompt | streaming_llm | StrOutputParser()
streaming_conv_chain = conv_prompt | streaming_llm | StrOutputParser()

def get_rag_chain():
    """Get RAG chain if vectorstore is ready"""
    vectorstore = get_vectorstore()
    if vectorstore is None:
        return None
    
    # Create retriever for RAG
    retriever = vectorstore.as_retriever(search_kwargs={"k": SEARCH_K})
    
    # Create RAG chain for system/app questions
    rag_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=None,  # Memory handled externally
        return_source_documents=False
    )
    return rag_chain

def get_streaming_rag_chain():
    """Get streaming RAG chain if vectorstore is ready"""
    vectorstore = get_vectorstore()
    if vectorstore is None:
        return None
    
    # Create retriever for RAG
    retriever = vectorstore.as_retriever(search_kwargs={"k": SEARCH_K})
    
    # Create streaming RAG chain for system/app questions
    rag_chain = ConversationalRetrievalChain.from_llm(
        llm=streaming_llm,
        retriever=retriever,
        memory=None,  # Memory handled externally
        return_source_documents=False
    )
    return rag_chain

async def stream_rag_response(query: str, chat_history):
    """Stream RAG response token by token"""
    rag_chain = get_streaming_rag_chain()
    if rag_chain is None:
        yield "My knowledge base is still loading. Please try again shortly."
        return
    
    try:
        async for chunk in rag_chain.astream({
            "question": query,
            "chat_history": chat_history
        }):
            if "answer" in chunk:
                yield chunk["answer"]
    except Exception as e:
        yield f"I'm sorry, I encountered an error while searching for information: {str(e)}"

async def stream_generation_response(query: str, chat_history: str):
    """Stream content generation response token by token"""
    try:
        async for chunk in streaming_gen_chain.astream({
            "query": query,
            "chat_history": chat_history
        }):
            yield chunk
    except Exception as e:
        yield f"I'm sorry, I encountered an error while generating content: {str(e)}"

async def stream_conversation_response(query: str, chat_history: str):
    """Stream conversation response token by token"""
    try:
        async for chunk in streaming_conv_chain.astream({
            "query": query,
            "chat_history": chat_history
        }):
            yield chunk
    except Exception as e:
        yield f"I'm sorry, I encountered an error while processing your message: {str(e)}"
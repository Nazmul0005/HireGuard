"""
Vector store operations for the chatbot application.
"""
import os
import threading
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from com.mhire.app.config.config import Config
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

config = Config()
model_name = config.model_name
openai_api_key = config.openai_api_key
KNOWLEDGE_BASE_PATH = config.knowledge_base_path
FAISS_INDEX_PATH = config.faiss_index_path

llm = ChatOpenAI(model=model_name, temperature=0.7)
embeddings = OpenAIEmbeddings()

# Global state for vector store
class VectorStoreState:
    def __init__(self):
        self.vectorstore = None
        self.is_loading = True
        self.load_error = None

vector_state = VectorStoreState()

def load_vectorstore_sync():
    """Synchronous version of load_vectorstore for background loading"""
    try:
        if os.path.exists(FAISS_INDEX_PATH) and os.listdir(FAISS_INDEX_PATH):
            print("Loading existing FAISS index...")
            vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
            print("FAISS index loaded successfully!")
            return vectorstore
        else:
            print("FAISS index not found. Creating new index from knowledge base...")
            return create_vectorstore()
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        print("Creating new index from knowledge base...")
        return create_vectorstore()

def load_vectorstore_background():
    """Load vector store in background thread"""
    try:
        print("Starting background vector store loading...")
        vector_state.vectorstore = load_vectorstore_sync()
        vector_state.is_loading = False
        print("Vector store loaded successfully in background!")
    except Exception as e:
        print(f"Error loading vector store in background: {e}")
        vector_state.load_error = str(e)
        vector_state.is_loading = False

def get_vectorstore():
    """Get vector store if ready, otherwise return None"""
    if vector_state.is_loading:
        return None
    if vector_state.load_error:
        raise Exception(f"Vector store failed to load: {vector_state.load_error}")
    return vector_state.vectorstore

def is_vectorstore_ready():
    """Check if vector store is ready"""
    return not vector_state.is_loading and vector_state.load_error is None

# Start loading vector store in background when module is imported
threading.Thread(target=load_vectorstore_background, daemon=True).start()

# Keep your existing create_vectorstore function unchanged
def create_vectorstore():
    """
    Create a new vector store from knowledge base documents.
   
    Returns:
        FAISS: The created vector store
    """
    try:
        # Load documents from knowledge base
        loader = DirectoryLoader(
            KNOWLEDGE_BASE_PATH,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader
        )
        documents = loader.load()
       
        if not documents:
            raise ValueError("No documents found in knowledge base directory")
       
        print(f"Loaded {len(documents)} documents from knowledge base")
       
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(documents)
       
        print(f"Split documents into {len(chunks)} chunks")
       
        # Create FAISS vector store
        vectorstore = FAISS.from_documents(chunks, embeddings)
       
        # Save to disk
        os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
        vectorstore.save_local(FAISS_INDEX_PATH)
       
        print("FAISS index created and saved successfully!")
        return vectorstore
       
    except Exception as e:
        print(f"Error creating vector store: {e}")
        raise e
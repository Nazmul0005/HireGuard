"""
Data ingestion script to create FAISS vector store from knowledge base documents.
"""

import os
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

def main():
    """
    Main function to ingest documents and create FAISS vector store.
    """
    # Load environment variables
    load_dotenv()
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    
    # Initialize embeddings
    
    # by default, it uses "text-embedding-3-small"
    # embeddings = OpenAIEmbeddings(model="text-embedding-3-large") ----> more accurate 

    embeddings = OpenAIEmbeddings()
    
    # Configuration
    KNOWLEDGE_BASE_PATH = "data/knowledge_base/"
    FAISS_INDEX_PATH = "faiss_index"
    # For small pdf like mine initiall 10 page -4000 words its better chatgpt says
    # chunk_size=500,     enough to fit a question + its answer
    # chunk_overlap=50,   mall overlap to not cut context
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    try:
        print("Starting document ingestion...")
        
        # Load documents from knowledge base
        loader = DirectoryLoader(
            KNOWLEDGE_BASE_PATH,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader
        )
        documents = loader.load()
        
        if not documents:
            print("No documents found in knowledge base directory!")
            return
        
        print(f"Loaded {len(documents)} documents from knowledge base")
        
        # Split documents into chunks
        # You can tune chunk_size so each Q&A pair fits as one chunk.-----------------------> chatgpt says check it.
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        chunks = text_splitter.split_documents(documents)
        
        print(f"Split documents into {len(chunks)} chunks")
        
        # Create FAISS vector store
        print("Creating FAISS vector store...")
        vectorstore = FAISS.from_documents(chunks, embeddings)
        
        # Save to disk
        os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
        vectorstore.save_local(FAISS_INDEX_PATH)
        
        print(f"FAISS index created and saved to {FAISS_INDEX_PATH}")
        print("Document ingestion completed successfully!")
        
    except Exception as e:
        print(f"Error during document ingestion: {e}")
        raise e

if __name__ == "__main__":
    main()
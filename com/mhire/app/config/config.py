import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            
            cls._instance = super(Config, cls).__new__(cls)

            cls._instance.openai_api_key = os.getenv("OPENAI_API_KEY")
            cls._instance.model_name = os.getenv("MODEL")
            cls._instance.model_name2 = os.getenv("MODEL2")
            cls._instance.chunk_size= os.getenv("CHUNK_SIZE")
            cls._instance.chunk_overlap= os.getenv("CHUNK_OVERLAP")
            cls._instance.search_k= os.getenv("SEARCH_K")
            cls._instance.knowledge_base_path= os.getenv("KNOWLEDGE_BASE_PATH")
            cls._instance.faiss_index_path= os.getenv("FAISS_INDEX_PATH")
            cls._instance.api_key = os.getenv("API_KEY")
            cls._instance.api_secret = os.getenv("API_SECRET")

            # Add other configuration parameters as needed
            cls._instance.fpp_create = os.getenv("FPP_CREATE")
            cls._instance.fpp_detect = os.getenv("FPP_DETECT")
            cls._instance.fpp_search = os.getenv("FPP_SEARCH")
            cls._instance.fpp_add = os.getenv("FPP_ADD")
            cls._instance.fpp_get_detail = os.getenv("FPP_GET_DETAIL")

            # MongoDB settings
            cls._instance.mongodb_uri = os.getenv("MONGODB_URI")
            cls._instance.mongodb_db = os.getenv("MONGODB_DB")
            cls._instance.mongodb_collection = os.getenv("MONGODB_COLLECTION")

        return cls._instance
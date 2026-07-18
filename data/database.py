import json
import random
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from src.config import settings, get_logger

logger = get_logger(__name__)

class DatabaseManager:
    """Manages all CRUD and semantic query configurations for ChromaDB."""
    
    def __init__(self):
        try:
            self.embeddings = OpenAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                api_key=settings.OPENAI_API_KEY
            )
            self.vector_store = Chroma(
                persist_directory=settings.CHROMA_PERSIST_DIR,
                embedding_function=self.embeddings
            )
        except Exception as e:
            logger.critical(f"Failed to initialize ChromaDB connection dependencies: {e}")
            raise

    def ingest_raw_json(self, json_file_path: str) -> bool:
        """Parses local historic data files and commits them to the vector engine."""
        try:
            with open(json_file_path, "r") as f:
                raw_data = json.load(f)
            
            documents = [
                Document(page_content=item["fact"], metadata={"sport": item["sport"]})
                for item in raw_data
            ]
            
            self.vector_store.add_documents(documents)
            logger.info(f"Ingested {len(documents)} factual records safely into vector database.")
            return True
        except Exception as e:
            logger.error(f"Ingestion lifecycle failed: {e}")
            return False

    def query_sampled_facts(self, topic: str, overfetch_k: int = 6, sample_k: int = 2) -> str:
        """Implements 'Over-Fetch & Sample' to force variety in RAG output."""
        try:
            logger.info(f"Executing over-fetch semantic query for topic: {topic}")
            results = self.vector_store.similarity_search(query=topic, k=overfetch_k)
            
            if not results:
                return "No historical local reference data found."
                
            sampled_docs = random.sample(results, min(sample_k, len(results)))
            return "\n".join([doc.page_content for doc in sampled_docs])
            
        except Exception as e:
            logger.error(f"Semantic similarity processing failed: {e}")
            return "Local database retrieval encountered an internal error."

db_manager = DatabaseManager()
import os
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http import models

load_dotenv()

class DesignMemory:
    def __init__(self):
        # 1. Use Google Embeddings
        self.embedding_model = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        self.collection_name = "JIVS_Design_System_Gemini" # New name to avoid conflict with old OpenAI vectors
        
        # Initialize Client
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
        )
        
        # Create Collection (Size 768 for Google 004 model)
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
            )

        # Initialize Vector Store
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embedding_model,
        )

    def add_template(self, description, metadata):
        from langchain_core.documents import Document
        doc = Document(page_content=description, metadata=metadata)
        self.vector_store.add_documents([doc])
        print(f"✅ Template stored: {metadata.get('name', 'Unknown')}")

    def find_similar_style(self, query, k=1):
        docs = self.vector_store.similarity_search(query, k=k)
        if docs:
            return docs[0]
        return None
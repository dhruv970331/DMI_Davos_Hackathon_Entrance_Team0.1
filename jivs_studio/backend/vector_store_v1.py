import os
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http import models

load_dotenv()

class DesignMemory:
    def __init__(self):
        self.embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
        self.collection_name = "JIVS_Design_System"
        
        # Initialize Client
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
        )
        
        # Create Collection if it doesn't exist
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
            )

        # Initialize Vector Store
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embedding_model,
        )

    def add_template(self, description, metadata):
        """
        Stores a design template.
        description: Text describing the visual style (what gets embedded).
        metadata: JSON containing technical details (colors, html snippet, image path).
        """
        from langchain_core.documents import Document
        
        doc = Document(page_content=description, metadata=metadata)
        self.vector_store.add_documents([doc])
        print(f"✅ Template stored: {metadata.get('name', 'Unknown')}")

    def find_similar_style(self, query, k=1):
        """
        Finds the most relevant design style based on user query.
        """
        docs = self.vector_store.similarity_search(query, k=k)
        if docs:
            return docs[0] # Return the best match
        return None
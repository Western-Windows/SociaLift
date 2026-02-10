from fastembed import LateInteractionTextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict
import uuid

# 1. Setup ColBERT Embedding Model
# We use FastEmbed specifically because it has a native Windows implementation of ColBERT.
# This model outputs lists of vectors per document, not just one vector.
embedding_model = LateInteractionTextEmbedding(model_name="colbert-ir/colbertv2.0")

# 2. Setup Qdrant Client (replaces Chroma)
# This creates a local file-based database, similar to Chroma's persist_directory.
client = QdrantClient(path="./my_qdrant_db") 
COLLECTION_NAME = "product_catalog"

def create_collection_if_not_exists():
    """
    Qdrant requires us to define the schema for ColBERT specifically because
    it uses 'multivector' storage.
    """
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=128,  # ColBERT v2 vectors are always size 128
                distance=models.Distance.COSINE,
                multivector_config=models.MultiVectorConfig(
                    comparator=models.MultiVectorComparator.MAX_SIM
                )
            )
        )

def index_documents(data_results: List[Dict]):
    """
    Takes your 'data_results' list of dicts and indexes them using ColBERT.
    """
    create_collection_if_not_exists()
    
    documents = [record['text'] for record in data_results]
    metadatas = [record['metadata'] for record in data_results]
    ids = [record.get('id', str(uuid.uuid4())) for record in data_results]

    # Convert text to ColBERT embeddings
    # This returns a generator, so we convert it to a list
    print("Generating ColBERT embeddings... this might take a moment.")
    embeddings = list(embedding_model.embed(documents))

    # Upload to Qdrant
    client.upload_collection(
        collection_name=COLLECTION_NAME,
        ids=ids,
        payload=metadatas,   # Your metadata (Gender, Category, etc.)
        vectors=embeddings,  # The multi-vectors
    )
    print(f"Successfully indexed {len(documents)} documents.")

def search_documents(query: str, top_k: int = 3):
    """
    Performs a ColBERT search. 
    Note: ColBERT doesn't just match keywords; it matches context very deeply.
    """
    # 1. Embed the query using the SAME model
    query_embeddings = list(embedding_model.query_embed(query))[0]

    # 2. Search Qdrant
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embeddings,
        limit=top_k,
        # You can add metadata filters here if needed:
        # query_filter=models.Filter(...) 
    )

    return results


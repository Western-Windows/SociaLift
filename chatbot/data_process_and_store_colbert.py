import pandas as pd
from pathlib import Path
# from data_embedding import store_in_vector_database, index_documents, load_vector_database
from data_embedding_colbert import index_documents,search_documents
from data_chunking import UniversalRAGIngestor
# from data_chunking import UniversalRAGIngestor
# Storing Pipeline
csv_path = Path("chatbot/fashion.csv")

df = pd.read_csv(csv_path)

results = UniversalRAGIngestor(df, "ProductTitle").process()

index_documents(results)

# Retrieval Pipeline
# vector_store = load_vector_database(persist_directory="./my_vector_db")

#Retrieval Logic
#Haneen's Code runs here, I'm just testing it
# query = "What are the available sizes of the Nike Air?"
# docs = vector_store.similarity_search(query, k=3)
# print(docs)
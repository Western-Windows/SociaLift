from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# 1. Setup your Embedding Model
# This downloads a small, free, high-quality model to your machine.
# You could also use OpenAIEmbeddings() here if you have an API key.
embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 2. Convert your dictionary output into LangChain "Documents"
# Your previous code produced a list of dicts. We need to wrap them.
# 'data_results' is the list returned by your UniversalRAGIngestor.process()
def store_in_vector_database(data_results): 
    docs = []
    for record in data_results:
        doc = Document(
            page_content=record['text'],  # The text we want to search against
            metadata=record['metadata'],  # The filters (Gender, Category, etc.)
            id=record['id']               # The unique ID
        )
        docs.append(doc)
    return docs

def index_documents(docs):
    vector_store = Chroma.from_documents(
        documents=docs, 
        embedding=embedding_function,
        persist_directory="./my_vector_db",  # Where to save on disk
        collection_name="product_catalog"
    )
    return vector_store

def load_vector_database(persist_directory):
    vector_store = Chroma(persist_directory=persist_directory, embedding_function=embedding_function,collection_name="product_catalog")
    return vector_store
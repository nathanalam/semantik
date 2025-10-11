from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from langchain.embeddings.huggingface import HuggingFaceBgeEmbeddings
from llama_index.core import Settings
import time
import os

start_time = time.time()

PERSIST_DIR = "./storage"

# global default
Settings.embed_model = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-base-en")
Settings.llm = None

print(f"{time.time() - start_time}: Starting program")

# Check if storage already exists
if not os.path.exists(PERSIST_DIR):
    print("Creating new index...")
    documents = SimpleDirectoryReader("pdfs").load_data()
    print(f"{time.time() - start_time}: Documents loaded")
    index = VectorStoreIndex.from_documents(documents)
    print(f"{time.time() - start_time}: Index created")
    # Store it for later
    index.storage_context.persist(persist_dir=PERSIST_DIR)
    print(f"{time.time() - start_time}: Index saved to disk")
else:
    print("Loading existing index from disk...")
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)
    print(f"{time.time() - start_time}: Index loaded from disk")

query_engine = index.as_query_engine()
print(f"{time.time() - start_time}: Query Engine ready")


while True:
    query = input("Enter a query:")
    response = query_engine.query(query)
    print(f"{time.time() - start_time}: Response loaded")
    print(response)

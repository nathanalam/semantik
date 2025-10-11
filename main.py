from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from langchain.embeddings.huggingface import HuggingFaceBgeEmbeddings
from llama_index.core import Settings
import time
import os

start_time = time.time()

PERSIST_DIR = "./storage"

# global default
Settings.embed_model = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-base-en-v1.5")
Settings.llm = None  # No LLM needed for pure retrieval

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

retriever = index.as_retriever(similarity_top_k=5)
print(f"{time.time() - start_time}: Retriever ready")


while True:
    query = input("Enter a query: ")
    nodes = retriever.retrieve(query)
    print(f"\n{time.time() - start_time}: Found {len(nodes)} relevant passages\n")
    
    for i, node in enumerate(nodes):
        print(f"--- Result {i+1} ---")
        print(f"Score: {node.score:.4f}")
        print(f"File: {node.node.metadata.get('file_path', 'Unknown')}")
        print(f"Page: {node.node.metadata.get('page_label', 'Unknown')}")
        print(f"Text:\n{node.node.text[:300]}...")
        print()

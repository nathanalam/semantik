from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from langchain.embeddings.huggingface import HuggingFaceBgeEmbeddings
from llama_index.core import Settings
import time

start_time = time.time()



# global default
Settings.embed_model = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-base-en")
Settings.llm = None

print(f"{time.time() - start_time}: Starting program")

print("Loading documents")
documents = SimpleDirectoryReader("pdfs").load_data()
print(f"{time.time() - start_time}: Documents loaded")
index = VectorStoreIndex.from_documents(documents)
print(f"{time.time() - start_time}: Index created")
query_engine = index.as_query_engine()
print(f"{time.time() - start_time}: Query Engine loaded")


while True:
    query = input("Enter a query:")
    response = query_engine.query(query)
    print(f"{time.time() - start_time}: Response loaded")
    print(response)

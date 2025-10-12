from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from llama_index.core import Settings
import os

PERSIST_DIR = "./storage"

Settings.embed_model = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-base-en-v1.5")
Settings.llm = None

if not os.path.exists(PERSIST_DIR):
    os.makedirs(PERSIST_DIR)

documents = SimpleDirectoryReader("pdfs").load_data()
index = VectorStoreIndex.from_documents(documents)
index.storage_context.persist(persist_dir=PERSIST_DIR)
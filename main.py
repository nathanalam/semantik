from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from llama_index.core import Settings
from llama_index.core.node_parser import SentenceSplitter
import os

PERSIST_DIR = "./storage"

Settings.embed_model = HuggingFaceBgeEmbeddings(model_name="Qwen/Qwen2.5-3B-Instruct")
Settings.llm = None
Settings.chunk_size = 512
Settings.chunk_overlap = 50
Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)

if not os.path.exists(PERSIST_DIR):
    os.makedirs(PERSIST_DIR)

documents = SimpleDirectoryReader("pdfs").load_data()
index = VectorStoreIndex.from_documents(documents)
index.storage_context.persist(persist_dir=PERSIST_DIR)

import streamlit as st
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from langchain.embeddings.huggingface import HuggingFaceBgeEmbeddings
from llama_index.core import Settings
import os
import fitz  # PyMuPDF
from PIL import Image
import io
import re

# Page config
st.set_page_config(page_title="PDF RAG Search", layout="wide")

PERSIST_DIR = "./storage"

# Initialize session state
if 'index' not in st.session_state:
    st.session_state.index = None
if 'retriever' not in st.session_state:
    st.session_state.retriever = None


@st.cache_resource
def load_or_create_index():
    """Load existing index or create new one"""
    # Configure settings
    Settings.embed_model = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-base-en-v1.5")
    Settings.llm = None  # No LLM needed for pure retrieval
    
    if not os.path.exists(PERSIST_DIR):
        with st.spinner("Creating new index from PDFs... This may take a minute..."):
            documents = SimpleDirectoryReader("pdfs").load_data()
            index = VectorStoreIndex.from_documents(documents)
            index.storage_context.persist(persist_dir=PERSIST_DIR)
        st.success("Index created and saved!")
    else:
        with st.spinner("Loading index from disk..."):
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            index = load_index_from_storage(storage_context)
        st.success("Index loaded!")
    
    return index


def find_text_in_pdf(pdf_path, search_text):
    """Search for text in PDF and return page numbers where it's found"""
    try:
        doc = fitz.open(pdf_path)
        pages_found = []
        # Take first 50 chars of search text as sample
        sample = search_text[:50].strip()
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if sample in text:
                pages_found.append(page_num + 1)  # Convert to 1-indexed
        
        doc.close()
        return pages_found
    except Exception:
        return []


def extract_pdf_references_from_nodes(nodes):
    """Extract PDF file paths and page numbers from retrieved nodes"""
    references = []
    
    for node in nodes:
        try:
            # Get metadata from node
            metadata = node.node.metadata if hasattr(node, 'node') else node.metadata
            
            file_path = metadata.get('file_path', '')
            page_label = metadata.get('page_label', '')
            text_content = node.node.text if hasattr(node, 'node') else node.text
            score = node.score if hasattr(node, 'score') else None
            
            if not file_path:
                continue
                
            try:
                page_num = int(page_label)
            except (ValueError, TypeError):
                page_num = 1
            
            # Validate and fix page numbers
            doc = fitz.open(file_path)
            num_pages = len(doc)
            doc.close()
            
            # If page number is out of range, try to find it by text
            if page_num < 1 or page_num > num_pages:
                found_pages = find_text_in_pdf(file_path, text_content[:50])
                if found_pages:
                    references.append({
                        'file_path': file_path,
                        'page_num': found_pages[0],
                        'original_page_label': page_num,
                        'text': text_content,
                        'score': score
                    })
            else:
                references.append({
                    'file_path': file_path,
                    'page_num': page_num,
                    'text': text_content,
                    'score': score
                })
        except Exception as e:
            st.warning(f"Error processing node: {e}")
            continue
    
    return references


def highlight_text_in_pdf(pdf_path, page_num, search_terms):
    """Render a PDF page with highlighted search terms"""
    doc = None
    try:
        doc = fitz.open(pdf_path)
        # Check if page number is valid (pages are 0-indexed internally)
        if page_num < 1 or page_num - 1 >= len(doc):
            num_pages = len(doc)
            if doc:
                doc.close()
            return None, f"Page {page_num} out of range (document has {num_pages} pages)"
        
        page = doc[page_num - 1]  # Convert to 0-indexed
        
        # Try to highlight search terms
        try:
            for term in search_terms:
                # Search for text instances
                text_instances = page.search_for(term)
                for inst in text_instances:
                    # Add yellow highlight
                    highlight = page.add_highlight_annot(inst)
                    highlight.set_colors(stroke=[1, 1, 0])  # Yellow
                    highlight.update()
        except Exception as highlight_error:
            # If highlighting fails, just log it and continue to render without highlights
            st.warning(f"Could not highlight text: {highlight_error}. Rendering page without highlights.")
        
        # Render page to image
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        doc.close()
        return img, None
    except Exception as e:
        if doc:
            doc.close()
        return None, str(e)


def extract_search_terms(query, response_text):
    """Extract meaningful search terms from query and response"""
    # Start with query words
    terms = set()
    
    # Add significant words from query (3+ chars, not common words)
    common_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with', 'to', 'for', 'of', 'as', 'by'}
    query_words = re.findall(r'\b\w{3,}\b', query.lower())
    for word in query_words:
        if word not in common_words:
            terms.add(word)
    
    # Try to extract key phrases (2-4 words) from the query
    query_clean = ' '.join(query_words)
    if len(query_clean.split()) <= 4:
        terms.add(query_clean)
    
    return list(terms)


# Main UI
st.title("📚 PDF Semantic Search")
st.markdown("Search your PDF documents using semantic similarity. Results are ranked by relevance.")

# Load index
if st.session_state.index is None:
    st.session_state.index = load_or_create_index()
    st.session_state.retriever = st.session_state.index.as_retriever(similarity_top_k=5)

# Sidebar - Number of results
with st.sidebar:
    st.header("⚙️ Settings")
    top_k = st.slider("Number of results to retrieve", min_value=1, max_value=10, value=5)
    
    # Update retriever if top_k changes
    if st.session_state.retriever is None or st.session_state.retriever.similarity_top_k != top_k:
        st.session_state.retriever = st.session_state.index.as_retriever(similarity_top_k=top_k)

# Query input
query = st.text_input("Enter your search query:", placeholder="e.g., par value, accrual accounting, revenue recognition")

if st.button("Search", type="primary") and query:
    with st.spinner("Searching..."):
        # Retrieve relevant nodes using semantic search
        nodes = st.session_state.retriever.retrieve(query)
        
        if nodes:
            st.success(f"Found {len(nodes)} relevant passages")
            
            # Extract references from nodes
            references = extract_pdf_references_from_nodes(nodes)
            
            if references:
                # Extract search terms for highlighting
                search_terms = extract_search_terms(query, "")
                
                # Display each reference
                for i, ref in enumerate(references):
                    pdf_path = ref['file_path']
                    page_num = ref['page_num']
                    filename = os.path.basename(pdf_path)
                    text_content = ref.get('text', '')
                    score = ref.get('score')
                    
                    # Create title with score if available
                    title = f"📖 {filename} - Page {page_num}"
                    if score is not None:
                        title += f" (Relevance: {score:.3f})"
                    if 'original_page_label' in ref:
                        title += f" [doc page {ref['original_page_label']}]"
                    
                    with st.expander(title, expanded=(i == 0)):
                        # Show relevance score
                        if score is not None:
                            st.metric("Relevance Score", f"{score:.4f}")
                        
                        st.markdown(f"**File:** `{filename}`")
                        st.markdown(f"**Page:** {page_num}")
                        
                        if 'original_page_label' in ref:
                            st.info(f"Note: Document internally numbered as page {ref['original_page_label']}, but found content on PDF page {page_num}")
                        
                        # Show retrieved text content
                        st.markdown("**Retrieved Text:**")
                        st.text_area("", text_content, height=150, disabled=True, key=f"text_{i}")
                        
                        # Render PDF with highlights
                        st.markdown("**PDF Page:**")
                        img, error = highlight_text_in_pdf(pdf_path, page_num, search_terms)
                        if img:
                            st.image(img, use_container_width=True)
                        else:
                            st.error(f"Could not render page {page_num} from {filename}: {error}")
            else:
                st.warning("Retrieved passages but could not process them.")
        else:
            st.info("No relevant passages found. Try a different search query.")




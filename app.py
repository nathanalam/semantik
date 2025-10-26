"""
PDF Semantic Search Viewer
"""

import streamlit as st
from llama_index.core import StorageContext, load_index_from_storage
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from llama_index.core import Settings
import os
import sys
import fitz  # PyMuPDF
import re
from streamlit_pdf_viewer import pdf_viewer

# Page config
st.set_page_config(page_title="Semantik PDF Viewer", layout="wide")

# Determine the base path for bundled resources
if getattr(sys, "frozen", False):
    # Running as compiled executable
    BASE_PATH = sys._MEIPASS
else:
    # Running as script
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

PERSIST_DIR = os.path.join(BASE_PATH, "storage")

# Initialize session state
if "index" not in st.session_state:
    st.session_state.index = None
if "retriever" not in st.session_state:
    st.session_state.retriever = None

# Add JavaScript for Ctrl+F to focus the search input
st.html("""
<script>
document.addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.key === 'f') {
        event.preventDefault();
        const inputs = document.querySelectorAll('input[type="text"]');
        if (inputs.length > 0) {
            inputs[0].focus();
        }
    }
});
</script>
""")


@st.cache_resource
def load_index():
    """Load existing index (read-only mode)"""
    # Configure settings
    Settings.embed_model = HuggingFaceBgeEmbeddings(
        model_name="ibm-granite/granite-embedding-278m-multilingual",
        model_kwargs={"device": "cuda"},
    )
    Settings.llm = None  # No LLM needed for pure retrieval

    if not os.path.exists(PERSIST_DIR):
        st.error(f"""
        ### ⚠️ Index Not Found

        The search index was not found at: `{PERSIST_DIR}`

        This application requires a pre-built index to function.
        Please ensure the index was included in the distribution.
        """)
        st.stop()

    try:
        with st.spinner("Loading search index..."):
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            index = load_index_from_storage(storage_context)
        st.success("✅ Search index loaded successfully!")
        return index
    except Exception as e:
        st.error(f"""
        ### ⚠️ Error Loading Index

        Failed to load the search index: {str(e)}

        The index files may be corrupted or incompatible.
        """)
        st.stop()


def extract_pdf_references_from_nodes(nodes):
    """Extract PDF file paths and page numbers from retrieved nodes"""
    references = []

    for node in nodes:
        try:
            # Get metadata from node
            metadata = node.node.metadata if hasattr(node, "node") else node.metadata

            file_path = metadata.get("file_path", "")
            page_label = metadata.get("page_label", "")
            text_content = node.node.text if hasattr(node, "node") else node.text
            score = node.score if hasattr(node, "score") else None

            if not file_path:
                continue

            # Convert to absolute path if running as executable
            if not os.path.isabs(file_path):
                file_path = os.path.join(BASE_PATH, file_path)

            # Check if file exists
            if not os.path.exists(file_path):
                st.warning(f"PDF file not found: {file_path}")
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
                    references.append(
                        {
                            "file_path": file_path,
                            "page_num": found_pages[0],
                            "original_page_label": page_num,
                            "text": text_content,
                            "score": score,
                        }
                    )
            else:
                references.append(
                    {
                        "file_path": file_path,
                        "page_num": page_num,
                        "text": text_content,
                        "score": score,
                    }
                )
        except Exception as e:
            st.warning(f"Error processing node: {e}")
            continue

    return references


@st.cache_data
def load_pdf_bytes(pdf_path):
    """Load PDF as bytes for the viewer"""
    with open(pdf_path, "rb") as f:
        return f.read()


def extract_search_terms(query, response_text):
    """Extract meaningful search terms from query and response"""
    # Start with query words
    terms = set()

    # Add significant words from query (3+ chars, not common words)
    common_words = {
        "the",
        "is",
        "at",
        "which",
        "on",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "with",
        "to",
        "for",
        "of",
        "as",
        "by",
    }
    query_words = re.findall(r"\b\w{3,}\b", query.lower())
    for word in query_words:
        if word not in common_words:
            terms.add(word)

    # Try to extract key phrases (2-4 words) from the query
    query_clean = " ".join(query_words)
    if len(query_clean.split()) <= 4:
        terms.add(query_clean)

    return list(terms)


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


def get_page_text(pdf_path, page_num):
    """Extract full text from a specific page for copyable display"""
    try:
        doc = fitz.open(pdf_path)
        page = doc[page_num - 1]  # Convert to 0-indexed
        text = page.get_text()
        doc.close()
        return text
    except Exception as e:
        return f"Error extracting text: {e}"


# Main UI
st.title("Semantik PDF Viewer")
st.markdown(
    "Search your PDF documents using semantic similarity. Results show relevant pages with highlights."
)

# Path to the PDF
pdf_path_dir = os.path.join(BASE_PATH, "pdfs")
pdf_files = os.listdir(pdf_path_dir)
pdf_path = os.path.join(pdf_path_dir, pdf_files[0])

if not os.path.exists(pdf_path):
    st.error("PDF file not found.")
    st.stop()

# Load index
if st.session_state.index is None:
    st.session_state.index = load_index()
    st.session_state.retriever = st.session_state.index.as_retriever(
        similarity_top_k=10
    )

# Sidebar - Number of results
with st.sidebar:
    st.header("⚙️ Settings")
    top_k = st.slider(
        "Number of results to retrieve", min_value=1, max_value=20, value=10
    )

    # Update retriever if top_k changes
    if (
        st.session_state.retriever is None
        or st.session_state.retriever.similarity_top_k != top_k
    ):
        st.session_state.retriever = st.session_state.index.as_retriever(
            similarity_top_k=top_k
        )


# Initialize session state for search query
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# Search input bar that looks like CTRL+F
search_query = st.text_input(
    "Search in PDF",
    placeholder="Enter text to find (Ctrl+F to focus)",
    key="search_input",
    value=st.session_state.search_query,
)

# Find pages to display
# Load PDF bytes
pdf_bytes = load_pdf_bytes(pdf_path)

if search_query and st.button("Search", type="primary"):
    st.session_state.search_query = search_query
    with st.spinner("Searching..."):
        # Retrieve relevant nodes using semantic search
        nodes = st.session_state.retriever.retrieve(search_query)

        if nodes:
            st.success(f"Found {len(nodes)} relevant passages")

            # Extract references from nodes
            references = extract_pdf_references_from_nodes(nodes)

            if references:
                # Extract search terms for highlighting
                search_terms = extract_search_terms(search_query, "")

                # Sort references by score descending
                sorted_references = sorted(
                    references, key=lambda r: r.get("score", 0), reverse=True
                )

                # Group references by page
                from collections import defaultdict

                page_to_refs = defaultdict(list)
                for ref in sorted_references:
                    page_to_refs[ref["page_num"]].append(ref)

                # Get pages sorted by max score per page
                page_scores = {
                    page: max(ref["score"] for ref in refs)
                    for page, refs in page_to_refs.items()
                }
                sorted_pages = sorted(page_scores, key=page_scores.get, reverse=True)

                # Interweave: for each page in order of significance, show passages then the page render and full text
                for page_num in sorted_pages:
                    with st.expander(
                        f"Page {page_num} - Matches & View", expanded=True
                    ):
                        # Show matching passages for this page
                        for ref in sorted(
                            page_to_refs[page_num],
                            key=lambda r: r["score"],
                            reverse=True,
                        ):
                            st.markdown(f"**Match (Score: {ref['score']:.3f})**")
                            st.text_area(
                                "",
                                ref.get("text", ""),
                                height=100,
                                disabled=True,
                                key=f"text_{page_num}_{hash(ref.get('text', ''))}",
                            )

                        # Show the PDF page
                        pdf_viewer(
                            pdf_bytes, pages_to_render=[page_num], render_text=True
                        )
            else:
                st.warning("Retrieved passages but could not process them.")
                # Show all pages if no references
                pdf_viewer(pdf_bytes, render_text=True)
        else:
            st.info("No relevant passages found. Try a different search query.")
            # Show all pages
            pdf_viewer(pdf_bytes, render_text=True)
else:
    # Show all pages without search
    pdf_viewer(pdf_bytes, render_text=True)

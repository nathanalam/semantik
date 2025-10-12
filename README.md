# Ragdoll

A pure vector-based semantic search system for PDF documents. Quickly find relevant passages in your PDFs using natural language queries, ranked by similarity.

## Features

- 🔍 **Pure semantic search** - No LLM inference, just fast vector similarity
- 💾 **Persistent index** - Build once, search instantly
- 📊 **Relevance scores** - See how well each result matches your query
- 🎨 **Interactive web UI** - Beautiful Streamlit interface
- 📄 **PDF rendering** - View actual PDF pages with highlighted search terms
- ⚙️ **Adjustable results** - Control how many passages to retrieve (1-10)
- ⚡ **Fast** - Uses efficient embedding-based retrieval
- 📦 **Standalone app** - Build distributable executables for macOS, Windows, and Linux

## Quick Start

### For Users (Pre-built Application)

If you received a pre-built application:

**macOS**: Double-click `Ragdoll.app`  
**Windows**: Run `Ragdoll.exe`  
**Linux**: Run `./Ragdoll` from terminal

### For Developers

1. **Install dependencies** using `uv`:
   ```bash
   uv sync
   ```

2. **Add your PDFs** to the `pdfs/` directory

3. **Generate the index** to generate the index:
   ```bash
   uv run main.py
   ```

## Usage

### Development Mode - Web App

Run the interactive web application:

```bash
uv run streamlit run app.py
```

This will open a browser window where you can:
- Enter search queries in natural language
- Adjust number of results to retrieve (1-10)
- View relevance scores for each result
- See the retrieved text passages
- View PDF pages with highlighted search terms
- Expand/collapse multiple source documents

### Development Mode - CLI

Run the command-line version:

```bash
uv run python main.py
```

Then enter queries when prompted. Results will show:
- Relevance scores
- Source file and page
- Text snippets from matching passages

## Building Executables

Want to create a standalone app? See **[PACKAGING.md](PACKAGING.md)** for complete instructions on:

- 📦 **Building executables** for macOS, Windows, and Linux
- 🔄 **Rebuilding the search index** when PDFs change
- 🚀 **Distributing** the application
- 🎨 **Customizing** icons and settings
- ⚙️ **Cross-platform** building strategies

### Quick Build

After creating your index with `uv run python main.py`:

**Manual macOS Build:**
```bash
# The Ragdoll.spec file includes PDFs and storage automatically
uv run streamlit-desktop-app build app.py --name Ragdoll --pyinstaller-options --hidden-import=tiktoken_ext.openai_public --hidden-import=tiktoken_ext --windowed --icon ./logo.icns
cp -r pdfs dist/Ragdoll.app/Contents/Frameworks/
cp -r storage dist/Ragdoll.app/Contents/Frameworks/
```

**Output:**
- macOS: `dist/Ragdoll.app`

## How It Works

1. **First Run**: Indexes all PDFs in `pdfs/` and saves to `./storage/` (~1 minute)
2. **Subsequent Runs**: Loads pre-built index from disk (seconds)
3. **Searching**: 
   - Your query is embedded using the same model as the documents
   - Vector similarity finds the most relevant passages
   - Results are ranked by cosine similarity score
4. **Display**: Shows retrieved text and renders PDF pages with highlights

## Rebuilding the Index

If you add, remove, or modify PDFs:

```bash
rm -rf ./storage
```

Then re-run the application to rebuild the index.
```
```bash
uv run main.py
```

## Technical Details

- **Embeddings**: BAAI/bge-base-en-v1.5 (768 dimensions)
- **Retrieval**: Pure vector similarity (no LLM)
- **PDF Processing**: PyMuPDF for rendering and highlighting
- **Storage**: Persistent vector index with metadata
- **UI Framework**: Streamlit
- **Package Manager**: uv (fast Python package manager)
- **Packaging**: PyInstaller

## Dependencies

All managed via `uv`:

- `llama-index` - Vector index and retrieval
- `langchain` - Embeddings integration  
- `streamlit` - Web interface
- `pymupdf` (fitz) - PDF rendering and highlighting
- `sentence-transformers` - Embedding models
- `pyinstaller` - Executable creation

## Notes

- ✅ No LLM required - this is pure semantic search
- ✅ The index is automatically saved to `./storage/` (excluded from git)
- ✅ Fast and efficient - suitable for large document collections
- ✅ Self-contained executables include Python runtime, models, PDFs, and index
- ✅ Works completely offline once built

### Resource Bundling

The macOS build uses a customized `Ragdoll.spec` file that automatically bundles:
- All PDFs from the `pdfs/` directory
- The search index from the `storage/` directory
- All required Python dependencies and models

When the app runs, it uses PyInstaller's `sys._MEIPASS` to locate these resources, making the app fully self-contained. No external dependencies needed!

## Documentation

- **[README.md](README.md)** - This file (features and development)
- **[PACKAGING.md](PACKAGING.md)** - Complete guide to building and distributing executables
- **[QUICKSTART.md](QUICKSTART.md)** - End-user guide for the pre-built application

## Contributing

This is a personal project, but suggestions are welcome via issues or pull requests.

## License

Open source - see LICENSE file for details.


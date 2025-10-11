# PDF Search Application - Packaging Guide

This guide explains how to rebuild the search index and create distributable executables for different platforms.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Rebuilding the Search Index](#rebuilding-the-search-index)
3. [Creating Executables](#creating-executables)
4. [Platform-Specific Instructions](#platform-specific-instructions)
5. [Distribution](#distribution)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Python 3.10-3.12** (3.13+ not yet supported by PyInstaller)
- **uv** package manager ([install from astral.sh](https://docs.astral.sh/uv/))
- Git (optional, for version control)

### Installation

1. Clone or download this repository
2. Navigate to the project directory:
   ```bash
   cd ragdoll
   ```

3. Install dependencies with uv:
   ```bash
   uv sync
   ```

---

## Rebuilding the Search Index

The search index must be rebuilt whenever you:
- Add new PDF files
- Remove PDF files
- Update existing PDF files

### Steps to Rebuild

1. **Add your PDF files** to the `pdfs/` directory:
   ```bash
   # Your PDFs should be in:
   pdfs/
   ├── document1.pdf
   ├── document2.pdf
   └── ...
   ```

2. **Delete the existing index** (if any):
   ```bash
   rm -rf storage
   ```

3. **Run the development app** to generate a new index:
   ```bash
   uv run streamlit run app.py
   ```

4. **Wait for index creation**: The app will display "Creating new index from PDFs..." 
   - This typically takes 1-2 minutes depending on the number and size of PDFs
   - Once complete, you'll see "Index created and saved!"

5. **Verify the index**:
   ```bash
   ls storage/
   # Should show: default__vector_store.json, docstore.json, graph_store.json, index_store.json
   ```

6. **Test the search**: Try a few queries to ensure the index works correctly

7. **Exit the app**: Press Ctrl+C in the terminal or close the browser tab

Now you're ready to build the executable!

---

## Creating Executables

### Quick Build (Current Platform)

Run the appropriate build script for your platform:

**macOS/Linux:**
```bash
./build.sh
```

**Windows:**
```cmd
build.bat
```

The script will:
1. ✅ Verify that `storage/` and `pdfs/` directories exist
2. 🧹 Clean previous builds
3. 📦 Run PyInstaller with the correct configuration
4. ✨ Create a distributable application

### Output Locations

- **macOS**: `dist/PDFSearch.app` (application bundle)
- **Linux**: `dist/PDFSearch/` (directory with executable)
- **Windows**: `dist/PDFSearch/` (directory with .exe)

---

## Platform-Specific Instructions

### macOS

#### Building on macOS

```bash
# From project root
./build.sh
```

#### Output
- **App Bundle**: `dist/PDFSearch.app`
- **Size**: ~500MB-1GB (includes Python runtime, embeddings model, PDFs, and index)

#### Running
```bash
open dist/PDFSearch.app
```

#### Distributing
1. Create a DMG or ZIP:
   ```bash
   cd dist
   zip -r PDFSearch-macOS.zip PDFSearch.app
   ```
2. Share `PDFSearch-macOS.zip`
3. Users extract and drag to Applications folder

#### Code Signing (Optional but Recommended)

For distribution outside the Mac App Store:

```bash
# Sign the app
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/PDFSearch.app

# Create notarization request
xcrun notarytool submit PDFSearch-macOS.zip --keychain-profile "notary-profile" --wait

# Staple the notarization
xcrun stapler staple dist/PDFSearch.app
```

### Linux

#### Building on Linux

```bash
# From project root
./build.sh
```

#### Output
- **Directory**: `dist/PDFSearch/`
- **Executable**: `dist/PDFSearch/PDFSearch`

#### Running
```bash
./dist/PDFSearch/PDFSearch
```

#### Distributing
1. Create tarball:
   ```bash
   cd dist
   tar -czf PDFSearch-Linux.tar.gz PDFSearch/
   ```
2. Share `PDFSearch-Linux.tar.gz`
3. Users extract and run the executable

#### Creating a .desktop File (Optional)

For better Linux integration:

```bash
cat > PDFSearch.desktop << EOF
[Desktop Entry]
Name=PDF Search
Comment=Semantic search for PDF documents
Exec=/path/to/PDFSearch/PDFSearch
Icon=/path/to/icon.png
Type=Application
Categories=Office;Utility;
EOF
```

### Windows

#### Building on Windows

```cmd
REM From project root
build.bat
```

#### Output
- **Directory**: `dist\PDFSearch\`
- **Executable**: `dist\PDFSearch\PDFSearch.exe`

#### Running
```cmd
dist\PDFSearch\PDFSearch.exe
```

#### Distributing
1. Compress the folder:
   - Right-click `dist\PDFSearch`
   - Send to → Compressed (zipped) folder
   - Rename to `PDFSearch-Windows.zip`
2. Share `PDFSearch-Windows.zip`
3. Users extract and run `PDFSearch.exe`

#### Creating an Installer (Optional)

Use **Inno Setup** or **NSIS** to create a proper Windows installer:

```iss
; Inno Setup script example
[Setup]
AppName=PDF Search
AppVersion=1.0
DefaultDirName={pf}\PDFSearch
DefaultGroupName=PDF Search
OutputBaseFilename=PDFSearchSetup

[Files]
Source: "dist\PDFSearch\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\PDF Search"; Filename: "{app}\PDFSearch.exe"
```

---

## Cross-Platform Building

### Building for Multiple Platforms

You **cannot** cross-compile with PyInstaller. To create executables for all platforms:

1. **Build on each target platform**:
   - macOS executable → Build on macOS
   - Windows executable → Build on Windows  
   - Linux executable → Build on Linux

2. **Use Virtual Machines or CI/CD**:
   - Use VirtualBox, Parallels, or VMware for other OS environments
   - Use GitHub Actions for automated multi-platform builds

### GitHub Actions Example

Create `.github/workflows/build.yml`:

```yaml
name: Build Executables

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    
    runs-on: ${{ matrix.os }}
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Install uv
      run: curl -LsSf https://astral.sh/uv/install.sh | sh
    
    - name: Build
      run: |
        uv sync
        ./build.sh  # or build.bat on Windows
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: PDFSearch-${{ matrix.os }}
        path: dist/
```

---

## Distribution

### File Sizes

Approximate compressed sizes:
- **macOS**: 400-800 MB
- **Windows**: 400-800 MB
- **Linux**: 400-800 MB

Size includes:
- Python runtime
- Streamlit and dependencies
- BGE embedding model (~400MB)
- PyMuPDF libraries
- Your PDF files
- Pre-built index

### Reducing Size

To create smaller distributions:

1. **Exclude PDFs** (users provide their own):
   - Remove `('pdfs', 'pdfs')` from `pdf_search.spec`
   - Update app to handle missing PDFs gracefully

2. **Use smaller embedding model**:
   - Change `BAAI/bge-base-en-v1.5` to `BAAI/bge-small-en-v1.5`
   - Rebuild index with new model

3. **Compress PDFs**:
   ```bash
   # Use ghostscript to compress PDFs
   gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
      -dNOPAUSE -dQUIET -dBATCH -sOutputFile=output.pdf input.pdf
   ```

### Hosting Options

For sharing large files:
- **Google Drive** / **Dropbox**: Easy, free for small teams
- **GitHub Releases**: Free, good for open source
- **AWS S3** / **Azure Blob**: Scalable, pay-as-you-go
- **WeTransfer**: Simple, up to 2GB free

---

## Troubleshooting

### Build Fails

**Problem**: "No module named 'streamlit'"
```bash
# Solution: Ensure dependencies are installed
uv sync
```

**Problem**: "storage directory not found"
```bash
# Solution: Create the index first
uv run streamlit run app.py
# Then rebuild after index is created
```

**Problem**: PyInstaller errors with Python 3.13+
```bash
# Solution: Use Python 3.10-3.12
uv python install 3.12
```

### App Won't Start

**macOS**: "App is damaged and can't be opened"
```bash
# Solution: Remove quarantine attribute
xattr -cr dist/PDFSearch.app
```

**Windows**: "Windows protected your PC"
- Click "More info" → "Run anyway"
- Or sign the executable (see Code Signing above)

**Linux**: "Permission denied"
```bash
# Solution: Make executable
chmod +x dist/PDFSearch/PDFSearch
```

### Search Not Working

**Problem**: "Index not found" error
- Verify `storage/` directory was included in build
- Check PyInstaller output for errors

**Problem**: "PDF file not found"
- Verify PDF paths in index match bundled PDF locations
- Rebuild index if PDFs were moved

**Problem**: Slow performance
- First search is always slower (model loading)
- Subsequent searches should be fast
- Consider using smaller embedding model

---

## Advanced Customization

### Custom Icon

1. Create an icon file:
   - macOS: `.icns` file (512x512)
   - Windows: `.ico` file (256x256)
   - Linux: `.png` file (256x256)

2. Update `pdf_search.spec`:
   ```python
   exe = EXE(
       ...
       icon='path/to/icon.ico',  # or .icns
       ...
   )
   ```

### Custom Window Title

Edit `app_readonly.py`:
```python
st.set_page_config(
    page_title="Your Custom Title",
    layout="wide"
)
```

### Exclude Sensitive PDFs

To build without certain PDFs:
```python
# In pdf_search.spec, be specific:
datas=[
    ('storage', 'storage'),
    ('pdfs/public_doc1.pdf', 'pdfs'),
    ('pdfs/public_doc2.pdf', 'pdfs'),
    # Don't include sensitive docs
],
```

Then rebuild index with only those PDFs.

---

## Version Management

Recommended workflow:

1. **Tag releases**:
   ```bash
   git tag -a v1.0.0 -m "Initial release"
   git push origin v1.0.0
   ```

2. **Document changes** in `CHANGELOG.md`

3. **Build for each version**:
   ```bash
   # Build and rename with version
   ./build.sh
   cd dist
   mv PDFSearch.app PDFSearch-v1.0.0.app
   zip -r PDFSearch-v1.0.0-macOS.zip PDFSearch-v1.0.0.app
   ```

---

## Support

For issues or questions:
1. Check this guide's Troubleshooting section
2. Review PyInstaller documentation: https://pyinstaller.org/
3. Check LlamaIndex docs: https://docs.llamaindex.ai/
4. Check Streamlit docs: https://docs.streamlit.io/

---

## License & Credits

Built with:
- **Streamlit** - Web framework
- **LlamaIndex** - RAG framework
- **PyInstaller** - Packaging tool
- **PyMuPDF** - PDF rendering
- **HuggingFace BGE** - Embeddings


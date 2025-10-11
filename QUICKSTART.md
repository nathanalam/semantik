# Quick Start Guide

## For End Users (Pre-built App)

### macOS
1. Download `PDFSearch-macOS.zip`
2. Extract the ZIP file
3. Drag `PDFSearch.app` to your Applications folder (optional)
4. Double-click `PDFSearch.app` to launch
5. If you see "App is damaged":
   ```bash
   xattr -cr /path/to/PDFSearch.app
   ```

### Windows
1. Download `PDFSearch-Windows.zip`
2. Extract the ZIP file
3. Double-click `PDFSearch.exe` inside the extracted folder
4. If Windows Defender blocks it, click "More info" → "Run anyway"

### Linux
1. Download `PDFSearch-Linux.tar.gz`
2. Extract the archive:
   ```bash
   tar -xzf PDFSearch-Linux.tar.gz
   ```
3. Run the application:
   ```bash
   cd PDFSearch
   ./PDFSearch
   ```

## Using the Application

1. **The app will open in your default web browser**
   - Don't worry, it's running locally - no internet needed!

2. **Enter a search query** in the text box
   - Example: "par value"
   - Example: "revenue recognition"
   - Example: "accrual accounting"

3. **Adjust settings** (optional)
   - Use the sidebar slider to change number of results (1-10)

4. **Click "Search"**
   - Results appear ranked by relevance
   - Each result shows:
     - Relevance score (higher = better match)
     - Source PDF and page number
     - Retrieved text passage
     - PDF page with highlighted search terms

5. **Explore results**
   - Click to expand/collapse each result
   - Scroll through PDF page images
   - Read the retrieved text

## Tips

- **Be specific**: "What is par value in accounting?" works better than just "value"
- **Use natural language**: The system understands context
- **Try variations**: If you don't find what you need, rephrase your query
- **Check all results**: Sometimes the best answer is in result #2 or #3

## Troubleshooting

### App won't start
- **macOS**: Remove quarantine with `xattr -cr PDFSearch.app`
- **Windows**: Allow through Windows Defender
- **Linux**: Make sure the file is executable: `chmod +x PDFSearch`

### Browser doesn't open
- The app may still be running. Check your browser manually:
  - Look for `http://localhost:8501` or similar
  - Open that URL manually

### No results found
- Try broader search terms
- Check spelling
- Try synonyms (e.g., "earnings" instead of "income")

### App is slow
- First search is always slower (loading models)
- Subsequent searches should be fast
- Large PDFs take longer to render

## Closing the App

- **Close the browser tab/window**
- **The app will automatically shut down** after a few seconds

Or:

- Find the terminal window (if visible)
- Press `Ctrl+C` to force quit

## Privacy & Security

✅ **Everything runs locally** - no data leaves your computer  
✅ **No internet required** - works completely offline  
✅ **No tracking** - we don't collect any data  
✅ **Your PDFs stay private** - never uploaded anywhere

## Need Help?

Contact your system administrator or the person who provided this application.

## Technical Details

- Built with Streamlit, LlamaIndex, and PyMuPDF
- Uses BAAI/bge-base-en-v1.5 embeddings
- Pure semantic search (no AI generation)
- Runs on Python 3.10-3.12


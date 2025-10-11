#!/bin/bash
# Build script for PDF Search application
# This script builds the application for the current platform (macOS/Linux)

set -e  # Exit on error

echo "🔨 Building PDF Search Application..."
echo ""

# Check if storage directory exists
if [ ! -d "storage" ]; then
    echo "❌ Error: 'storage' directory not found!"
    echo "Please run the app first to generate the index, or follow the README to create it."
    exit 1
fi

# Check if pdfs directory exists
if [ ! -d "pdfs" ]; then
    echo "❌ Error: 'pdfs' directory not found!"
    echo "Please ensure your PDF files are in the 'pdfs' directory."
    exit 1
fi

echo "✅ Found storage directory"
echo "✅ Found pdfs directory"
echo ""

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist 2>/dev/null || true
echo ""

# Run PyInstaller
echo "📦 Running PyInstaller..."
uv run pyinstaller pdf_search.spec

echo ""
echo "✅ Build complete!"
echo ""
echo "📍 Output location:"

if [ "$(uname)" == "Darwin" ]; then
    # macOS
    echo "   macOS App: ./dist/PDFSearch.app"
    echo ""
    echo "To run the app:"
    echo "   open ./dist/PDFSearch.app"
    echo ""
    echo "To distribute:"
    echo "   1. Compress: cd dist && zip -r PDFSearch-macOS.zip PDFSearch.app"
    echo "   2. Share the .zip file"
else
    # Linux
    echo "   Linux Binary: ./dist/PDFSearch/PDFSearch"
    echo ""
    echo "To run the app:"
    echo "   ./dist/PDFSearch/PDFSearch"
    echo ""
    echo "To distribute:"
    echo "   1. Compress: cd dist && tar -czf PDFSearch-Linux.tar.gz PDFSearch"
    echo "   2. Share the .tar.gz file"
fi

echo ""
echo "🎉 Done!"


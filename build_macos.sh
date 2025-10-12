#!/bin/bash
# Build script for Ragdoll macOS app
# This script properly bundles PDFs and storage into the Streamlit desktop app

set -e  # Exit on error

echo "🧹 Cleaning previous build..."
rm -rf dist/Ragdoll.app dist/Ragdoll build/Ragdoll

# Check if storage and pdfs exist
if [ ! -d "storage" ]; then
    echo "❌ Error: storage directory not found!"
    echo "Please run 'uv run python main.py' first to create the index."
    exit 1
fi

if [ ! -d "pdfs" ] || [ -z "$(ls -A pdfs)" ]; then
    echo "❌ Error: pdfs directory not found or empty!"
    echo "Please add PDF files to the pdfs/ directory first."
    exit 1
fi

echo "🔨 Building macOS app with streamlit-desktop-app..."
uv run streamlit-desktop-app build app.py --name Ragdoll --pyinstaller-options --hidden-import=tiktoken_ext.openai_public --hidden-import=tiktoken_ext --windowed --icon ./logo.icns

echo "📦 Copying PDFs and storage to app bundle..."
# For .app bundles, resources go into Contents/Resources/
cp -r pdfs dist/Ragdoll.app/Contents/Frameworks/
cp -r storage dist/Ragdoll.app/Contents/Frameworks/

echo "✅ Build complete!"
echo "📍 App location: dist/Ragdoll.app"
echo "📦 PDFs and storage are bundled inside the app"
echo ""
echo "To test the app, run:"
echo "  open dist/Ragdoll.app"


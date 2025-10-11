@echo off
REM Build script for PDF Search application (Windows)

echo 🔨 Building PDF Search Application...
echo.

REM Check if storage directory exists
if not exist "storage" (
    echo ❌ Error: 'storage' directory not found!
    echo Please run the app first to generate the index, or follow the README to create it.
    exit /b 1
)

REM Check if pdfs directory exists
if not exist "pdfs" (
    echo ❌ Error: 'pdfs' directory not found!
    echo Please ensure your PDF files are in the 'pdfs' directory.
    exit /b 1
)

echo ✅ Found storage directory
echo ✅ Found pdfs directory
echo.

REM Clean previous builds
echo 🧹 Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
echo.

REM Run PyInstaller
echo 📦 Running PyInstaller...
uv run pyinstaller pdf_search.spec

echo.
echo ✅ Build complete!
echo.
echo 📍 Output location:
echo    Windows Executable: .\dist\PDFSearch\PDFSearch.exe
echo.
echo To run the app:
echo    .\dist\PDFSearch\PDFSearch.exe
echo.
echo To distribute:
echo    1. Compress the dist\PDFSearch folder into a .zip file
echo    2. Share the .zip file
echo.
echo 🎉 Done!



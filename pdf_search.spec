# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app_readonly.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('storage', 'storage'),
        ('pdfs', 'pdfs'),
    ],
    hiddenimports=[
        'streamlit',
        'streamlit.runtime.scriptrunner.magic_funcs',
        'llama_index.core',
        'llama_index.core.indices',
        'llama_index.core.storage',
        'langchain.embeddings.huggingface',
        'sentence_transformers',
        'fitz',
        'PIL',
        'torch',
        'transformers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PDFSearch',
    debug=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='PDFSearch',
)

app = BUNDLE(
    coll,
    name='PDFSearch.app',
    icon=None,
    bundle_identifier='com.pdfsearch.app',
)

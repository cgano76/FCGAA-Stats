import json
import re
import sys
from pathlib import Path


ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

EXTERNAL_FILES = [
    Path("S:/FCGAA/Stat Nationales/Campagnes/2026/Rapports/Statistiques FCGAA 2026 - Exercices 2025_compressed.pdf"),
    Path("S:/FCGAA/Stat Nationales/Campagnes/2026/Rapports/Statistiques FCGAA 2025 - Exercices 2024_compressed.pdf"),
    Path("S:/FCGAA/Stat Nationales/Campagnes/2026/Rapports/Dico Calculs.pdf"),
    Path("S:/FCGAA/Stat Nationales/Campagnes/2026/Rapports/Dico Importation.pdf"),
    Path("S:/FCGAA/Stat Nationales/Campagnes/2026/Rapports/STATISTIQUES_FCGAA.txt"),
    Path("S:/FCGAA/Stat Nationales/Exports Editeurs/EXPORTATION_DICTIONNAIRE.xlsx"),
]

LOCAL_PATTERNS = [
    "README.md",
    "docs/**/*.md",
    "docs/**/*.txt",
    ".env.example",
    "docker-compose.yml",
]


def clean_text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def chunks(text, size=1100, overlap=180):
    text = clean_text(text)
    if not text:
        return []
    result = []
    start = 0
    while start < len(text) and len(result) < 60:
        result.append(text[start : start + size])
        start += max(1, size - overlap)
    return result


def read_text_file(path):
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=encoding, errors="ignore")
        except Exception:
            continue
    return ""


def read_pdf(path):
    try:
        from pypdf import PdfReader
    except Exception:
        return []
    try:
        reader = PdfReader(str(path))
    except Exception:
        return []
    docs = []
    for index, page in enumerate(reader.pages[:120], start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        for chunk_index, chunk in enumerate(chunks(text, size=1000, overlap=120), start=1):
            docs.append({
                "title": path.name,
                "path": str(path),
                "type": "pdf",
                "page": index,
                "chunk": chunk_index,
                "text": chunk,
            })
    return docs


def read_xlsx_dictionary(path):
    try:
        sys.path.insert(0, str(ROOT))
        from scripts.extract_txt import dictionary_columns
        columns = dictionary_columns(str(path))
    except Exception:
        return []
    text = "\n".join(f"Position {col.get('position')} : {col.get('label')} ({col.get('type')})" for col in columns)
    return [{
        "title": path.name,
        "path": str(path),
        "type": "xlsx",
        "page": "",
        "chunk": 1,
        "text": chunk,
    } for chunk in chunks(text, size=1200, overlap=100)]


def add_text_document(documents, path, title=None, doc_type="texte"):
    text = read_text_file(path)
    for index, chunk in enumerate(chunks(text), start=1):
        documents.append({
            "title": title or path.name,
            "path": str(path),
            "type": doc_type,
            "page": "",
            "chunk": index,
            "text": chunk,
        })


def build_index():
    documents = []
    seen = set()
    for pattern in LOCAL_PATTERNS:
        for path in ROOT.glob(pattern):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            add_text_document(documents, path, doc_type="projet")

    for path in EXTERNAL_FILES:
        if not path.exists():
            continue
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            documents.extend(read_pdf(path))
        elif suffix == ".xlsx":
            documents.extend(read_xlsx_dictionary(path))
        else:
            add_text_document(documents, path, doc_type="source")

    return documents[:900]


if __name__ == "__main__":
    print(json.dumps({"documents": build_index()}, ensure_ascii=False))

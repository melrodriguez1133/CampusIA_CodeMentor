"""Ingesta y recuperación local de apuntes: PDF, DOCX, TXT y Markdown.

No guarda documentos en disco. Los fragmentos se conservan únicamente en
la memoria de sesión de Streamlit. Recuperación léxica BM25, sin embeddings.
"""
from collections import Counter
from io import BytesIO
import math
from pathlib import Path
import re
import unicodedata

from .models import KnowledgeChunk

STOP_WORDS = {
    "a", "al", "algo", "como", "con", "cual", "cuando", "de", "del", "desde",
    "donde", "el", "en", "es", "esta", "este", "esto", "fue", "ha", "hay",
    "la", "las", "le", "lo", "los", "mas", "me", "mi", "mis", "no", "o",
    "para", "por", "que", "se", "ser", "si", "son", "su", "sus", "te", "tiene",
    "tu", "un", "una", "unos", "y", "ya", "explica", "quiero", "sobre", "puedes",
}
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


def tokenize(text: str) -> list[str]:
    """Normaliza acentos y conserva números y términos técnicos."""
    normalized = unicodedata.normalize("NFKD", text.lower())
    normalized = "".join(c for c in normalized if not unicodedata.combining(c))
    return [w for w in re.findall(r"[a-z0-9_]+", normalized) if len(w) > 1 and w not in STOP_WORDS]


def chunk_text(text: str, source: str, page: int | None = None,
               size: int = 1250, overlap: int = 180) -> list[KnowledgeChunk]:
    """Divide sin perder trazabilidad; solapa para preservar contexto."""
    if size <= overlap or overlap < 0:
        raise ValueError("El solapamiento debe ser menor que el tamaño del fragmento.")
    cleaned = re.sub(r"[ \t]+", " ", text).strip()
    if not cleaned:
        return []
    chunks: list[KnowledgeChunk] = []
    start = 0
    while start < len(cleaned):
        end = min(start + size, len(cleaned))
        if end < len(cleaned):
            split = cleaned.rfind(" ", start + size // 2, end)
            if split > start:
                end = split
        value = cleaned[start:end].strip()
        if value:
            chunks.append(KnowledgeChunk(source, page, len(chunks) + 1, value))
        if end >= len(cleaned):
            break
        start = max(start + 1, end - overlap)
    return chunks


def read_document(filename: str, data: bytes, max_mb: int = 8) -> list[KnowledgeChunk]:
    """Extrae texto de un archivo permitido, sin ejecutar su contenido."""
    safe_name = filename.replace("\\", "/").split("/")[-1][:130]
    suffix = Path(safe_name).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError("Formato no admitido. Usa PDF, DOCX, TXT o MD.")
    if len(data) > max_mb * 1024 * 1024:
        raise ValueError(f"El archivo supera el límite de {max_mb} MB.")
    if not data:
        raise ValueError("El archivo está vacío.")

    if suffix in {".txt", ".md"}:
        raw = data.decode("utf-8-sig", errors="replace")
        chunks = chunk_text(raw, safe_name)
    elif suffix == ".docx":
        from docx import Document
        document = Document(BytesIO(data))
        paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
        for table in document.tables:
            paragraphs.extend(" | ".join(c.text for c in row.cells) for row in table.rows)
        chunks = chunk_text("\n".join(paragraphs), safe_name)
    else:
        from pypdf import PdfReader
        pdf = PdfReader(BytesIO(data))
        if pdf.is_encrypted:
            raise ValueError("PDF protegido: primero desbloquéalo con autorización.")
        if len(pdf.pages) > 60:
            raise ValueError("El PDF supera las 60 páginas permitidas en este taller.")
        chunks = []
        for page_num, page in enumerate(pdf.pages, start=1):
            text = (page.extract_text() or "")[:140_000]
            chunks.extend(chunk_text(text, safe_name, page=page_num))
    if not chunks:
        raise ValueError("No se encontró texto legible; los PDF escaneados requieren OCR.")
    return chunks


def retrieve(query: str, chunks: list[KnowledgeChunk], limit: int = 3) -> list[KnowledgeChunk]:
    """Selecciona fragmentos relevantes con BM25, sin servicios externos."""
    terms = set(tokenize(query))
    if not terms or not chunks:
        return []
    document_terms = [Counter(tokenize(c.text)) for c in chunks]
    lengths = [sum(freq.values()) for freq in document_terms]
    avg_len = max(1.0, sum(lengths) / len(lengths))
    n = len(chunks)
    df = Counter(term for freq in document_terms for term in freq)
    rankings: list[tuple[float, int]] = []
    k1, b = 1.5, 0.75
    for idx, freq in enumerate(document_terms):
        score = 0.0
        for term in terms:
            f = freq.get(term, 0)
            if not f:
                continue
            idf = math.log(1.0 + (n - df[term] + 0.5) / (df[term] + 0.5))
            score += idf * f * (k1 + 1) / (f + k1 * (1 - b + b * lengths[idx] / avg_len))
        if score > 0:
            rankings.append((score, idx))
    rankings.sort(reverse=True)
    return [chunks[idx] for _score, idx in rankings[:max(0, limit)]]


def load_example_chunks(language: str = "Python") -> list[KnowledgeChunk]:
    """Carga una muestra relevante al lenguaje; nunca se necesita subir datos privados."""
    from .learning_catalog import roadmap_topics

    filenames = {"Python": "apuntes_python.txt", "JavaScript": "apuntes_javascript.txt",
                 "Java": "apuntes_java.txt", "SQL": "apuntes_sql.txt"}
    filename = filenames.get(language)
    if filename:
        path = Path(__file__).resolve().parent.parent / "ejemplos" / filename
        if path.is_file():
            return read_document(filename, path.read_bytes())
    topics = ", ".join(roadmap_topics(language))
    text = (f"Guía inicial de {language}. Temas sugeridos: {topics}. "
            "Practica con un programa pequeño, identifica entradas y salidas, "
            "y explica cada paso de tu solución.")
    return chunk_text(text, f"guia_{language.lower().replace(' ', '_')}.txt")

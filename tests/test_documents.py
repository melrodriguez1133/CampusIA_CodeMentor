from io import BytesIO
from pathlib import Path
import pytest

from campusia.documents import chunk_text, load_example_chunks, read_document, retrieve, tokenize


def test_tokenization_accents():
    assert "programacion" in tokenize("Programación")
    assert "javascript" in tokenize("¿Qué hace JavaScript?")


def test_chunking_has_sources():
    chunks = chunk_text("Variables y funciones en Python. " * 300, "mis_notas.txt", size=160, overlap=20)
    assert len(chunks) > 1
    assert chunks[0].label.startswith("mis_notas.txt")
    assert all(len(part.text) <= 160 for part in chunks)


def test_rank_finds_specific_python_material():
    selected = retrieve("funciones en Python", load_example_chunks("Python"))
    assert selected and "python" in selected[0].source


def test_switch_material_by_language():
    selected = retrieve("función y array JavaScript", load_example_chunks("JavaScript"))
    assert selected and "javascript" in selected[0].source


def test_generic_language_example():
    selected = load_example_chunks("Kotlin")
    assert selected and "Kotlin" in selected[0].text


def test_unknown_topic_returns_empty():
    assert retrieve("xilófono arqueología", load_example_chunks()) == []


def test_read_text_file():
    chunks = read_document("guia.txt", "Una función toma parámetros".encode())
    assert "función" in chunks[0].text


def test_disallowed_extensions_and_empty():
    with pytest.raises(ValueError):
        read_document("ejecutar.py", b"print(1)")
    with pytest.raises(ValueError):
        read_document("vacio.txt", b"")


def test_docx_parsing():
    from docx import Document
    doc = Document()
    doc.add_paragraph("Java permite definir clases y métodos")
    data = BytesIO()
    doc.save(data)
    assert "clases" in read_document("resumen.docx", data.getvalue())[0].text


def test_pdf_parsing_with_mock_reader(monkeypatch):
    """Verifica la lógica de extracción sin depender de un PDF de muestra externo."""
    from pypdf import PdfReader

    class Page:
        def extract_text(self):
            return "Python permite escribir funciones y usar listas de datos."

    class FakePdfReader:
        is_encrypted = False
        pages = [Page()]
        def __init__(self, file):
            pass

    monkeypatch.setattr("pypdf.PdfReader", FakePdfReader)
    chunks = read_document("guia.pdf", b"contenido simulado")
    assert chunks[0].page == 1
    assert retrieve("funciones Python", chunks)

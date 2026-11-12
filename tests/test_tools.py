from datetime import date
import pytest

from campusia.learning_catalog import LANGUAGES, roadmap_topics, starter_code
from campusia.tools import build_learning_plan, demo_exam, inspect_python


def test_syntax_checker_valid():
    assert "sintaxis de Python es válida" in inspect_python("def hola():\n    return 'ok'")


def test_syntax_checker_bad():
    assert "Error de sintaxis" in inspect_python("def hola()\n    return 'ok'")


def test_plan_covers_duration():
    result = build_learning_plan("Python", "Variables, Bucles, Funciones", 7, 2,
                                 goal="Aprender bases", today=date(2026, 11, 12))
    assert result.count("**Día ") == 7
    assert "12/11/2026" in result
    assert "18/11/2026" in result
    assert "Python" in result and "proyecto" in result


def test_plan_auto_topics():
    result = build_learning_plan("Rust", "", 14, 1, today=date(2026, 11, 12))
    assert "Ownership" in result


def test_plan_rejects_invalid_duration():
    with pytest.raises(ValueError):
        build_learning_plan("Python", "Funciones", 0, 2)
    with pytest.raises(ValueError):
        build_learning_plan("Python", "Funciones", 46, 2)


def test_plan_rejects_too_many_topics():
    with pytest.raises(ValueError):
        build_learning_plan("JavaScript", ",".join(f"Tema {n}" for n in range(31)), 14, 1)


def test_plan_defaults_are_real_languages():
    assert "Python" in LANGUAGES and "JavaScript" in LANGUAGES and "SQL" in LANGUAGES
    assert len(roadmap_topics("Java")) >= 5
    assert "SELECT" in starter_code("SQL")


def test_demo_quiz_labeled():
    text = demo_exam("Funciones", 5)
    assert "modo demostración" in text
    assert "5." in text

"""Autoverificación local de arquitectura sin modelo ni acceso a internet."""
from datetime import date

from campusia.agent import UniversityAgent
from campusia.documents import load_example_chunks, retrieve
from campusia.models import StudentProfile
from campusia.providers import DemoProvider
from campusia.tools import build_learning_plan, inspect_python


def main():
    materials = load_example_chunks("Python")
    assert retrieve("función en Python", materials)
    assert "Error de sintaxis" in inspect_python("def hola()\n    pass")
    assert "Plan diario" in build_learning_plan("Java", "", 7, 1.5, today=date.today())
    response = UniversityAgent(DemoProvider()).chat("¿Qué es función en Python?", StudentProfile(), materials)
    assert response.sources
    print("OK: documentos, recuperación, sintaxis, plan y chat de demostración.")
    print("Para abrir CampusIA: python -m streamlit run app.py")


if __name__ == "__main__":
    main()

from campusia.agent import UniversityAgent
from campusia.documents import load_example_chunks
from campusia.models import StudentProfile
from campusia.providers import DemoProvider, LLMProvider


class FakeProvider(LLMProvider):
    name = "Proveedor de prueba"

    def __init__(self):
        self.received = None

    def generate(self, system, user, history=()):
        self.received = (system, user, history)
        return "Explicación ilustrativa de variables y funciones."


def test_chat_uses_programming_language_profile():
    fake = FakeProvider()
    agent = UniversityAgent(fake)
    result = agent.chat("Explícame los tipos", StudentProfile(language="JavaScript"))
    assert "JavaScript" in fake.received[0]
    assert "lenguajes de programación" in fake.received[0].lower()
    assert result.text


def test_agent_retrieves_material_and_exact_labels():
    fake = FakeProvider()
    result = UniversityAgent(fake).chat("¿Qué es una función en Python?", StudentProfile(), load_example_chunks())
    assert result.sources
    assert "FUENTE" in fake.received[1]
    assert "apuntes_python.txt" in result.sources[0]


def test_agent_syntax_check_without_code_execution():
    fake = FakeProvider()
    result = UniversityAgent(fake).chat("```python\ndef hola()\n  pass\n```", StudentProfile())
    assert "Error de sintaxis" in result.text
    assert "Revisión sintáctica" in result.steps[0]


def test_chat_regular_question_goes_to_model():
    fake = FakeProvider()
    result = UniversityAgent(fake).chat("¿Cómo programo un juego simple?", StudentProfile())
    assert fake.received is not None
    assert result.text


def test_demo_no_fake_original_answers():
    result = UniversityAgent(DemoProvider()).chat("Enséñame Python", StudentProfile())
    assert "Modo demostración" in result.text


def test_demo_excerpts_from_python_notes():
    result = UniversityAgent(DemoProvider()).chat(
        "¿Qué es una función Python?", StudentProfile(), load_example_chunks())
    assert "Fragmentos recuperados" in result.text
    assert "apuntes_python.txt" in result.text


def test_exam_topics_include_selected_language():
    fake = FakeProvider()
    UniversityAgent(fake).exam("condicionales", 4, StudentProfile(language="JavaScript"))
    assert "JavaScript" in fake.received[1]


def test_demo_challenges_are_labeled():
    result = UniversityAgent(DemoProvider()).exam("funciones", 3, StudentProfile())
    assert "modo demostración" in result.text.lower()


def test_review_non_python_avoids_fake_parser():
    fake = FakeProvider()
    UniversityAgent(fake).code_help("console.log('hola')", StudentProfile(language="JavaScript"))
    assert "No hay analizador sintáctico local" in fake.received[1]


def test_review_python_finds_real_syntax_error():
    fake = FakeProvider()
    result = UniversityAgent(fake).code_help("def hola()\n    pass", StudentProfile())
    assert "Error de sintaxis" in result.text


def test_no_executing_student_code():
    fake = FakeProvider()
    marker = 'raise RuntimeError("No debe ejecutarse")'
    UniversityAgent(fake).code_help(marker, StudentProfile())
    assert "no" in fake.received[1].lower()  # instrucciones explícitas de no ejecutar

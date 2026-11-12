"""Contratos de datos tipados para el mentor de programación."""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class StudentProfile:
    """Preferencias didácticas de una sesión; no contienen datos privados."""
    language: str = "Python"
    level: str = "Principiante"
    goal: str = "Aprender desde cero y crear mi primer proyecto"
    learning_style: str = "Paso a paso y con ejemplos"


@dataclass(frozen=True)
class KnowledgeChunk:
    """Fragmento de material de estudio con referencia verificable."""
    source: str
    page: int | None
    index: int
    text: str

    @property
    def label(self) -> str:
        page_text = f", pág. {self.page}" if self.page is not None else ""
        return f"{self.source}{page_text}, fragmento {self.index}"


@dataclass
class AgentResponse:
    """Texto y fuentes consultadas; pasos de diagnóstico para pruebas internas."""
    text: str
    steps: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)

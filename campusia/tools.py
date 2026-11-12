"""Herramientas educativas deterministas. NUNCA ejecutan código del estudiante."""
import ast
from datetime import date, timedelta
import re

from .learning_catalog import roadmap_topics


def inspect_python(code: str) -> str:
    """Usa el parser de Python para revisar solo sintaxis, sin ejecutarla."""
    if not code.strip():
        return "Pega un fragmento de Python para comprobar su sintaxis."
    if len(code) > 15_000:
        return "El fragmento supera el máximo de 15.000 caracteres."
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        snippet = (exc.text or "").strip()
        return (
            f"❌ Error de sintaxis en línea {exc.lineno}, columna {exc.offset}: "
            f"{exc.msg}.\n\nLínea: `{snippet}`\n\n"
            "**Pista:** revisa los dos puntos, la indentación, las comillas y los paréntesis."
        )
    functions = sum(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) for node in ast.walk(tree))
    return (
        f"✅ La sintaxis de Python es válida: {len(code.splitlines())} líneas, "
        f"{functions} funciones. Esto no comprueba la lógica: **el código no se ejecutó**."
    )


def build_learning_plan(language: str, topics_raw: str, days: int,
                        hours_per_day: float, goal: str = "",
                        today: date | None = None) -> str:
    """Crea un plan práctico y reproducible de 1 a 45 días sin usar un LLM."""
    if not 1 <= days <= 45:
        raise ValueError("El plan debe durar entre 1 y 45 días.")
    if not 0.5 <= hours_per_day <= 8:
        raise ValueError("Dedica entre media hora y 8 horas al día.")
    topics = [item.strip() for item in re.split(r"[,;\n]+", topics_raw) if item.strip()]
    if not topics:
        topics = list(roadmap_topics(language))
    if len(topics) > 30:
        raise ValueError("Elige hasta 30 temas para tu plan.")
    today = today or date.today()
    start = today.strftime("%d/%m/%Y")
    end = (today + timedelta(days=days - 1)).strftime("%d/%m/%Y")
    total_minutes = int(hours_per_day * 60)
    example_day = max(1, days - 1)
    lines = [
        f"# Ruta de aprendizaje · {language}",
        "",
        f"**Período:** {start} al {end} · **Duración:** {days} día(s) · "
        f"**Dedicación:** {hours_per_day:g} h/día",
        f"**Objetivo:** {goal.strip() or 'Aprender fundamentos y construir un mini proyecto'}",
        "",
        "## Plan diario",
        "",
    ]
    for index in range(days):
        current = today + timedelta(days=index)
        topic = topics[min(len(topics) - 1, index * len(topics) // max(1, example_day))]
        if index == days - 1 and days > 1:
            activity = "**Entrega:** integra lo aprendido en un mini proyecto y explica tu solución"
        elif index > 0 and index % 5 == 4:
            activity = f"**Repaso activo:** vuelve a {topic}, corrige errores y resuelve un reto sin apuntes"
        else:
            activity = f"**{topic}:** aprende un concepto, escribe código propio y resuelve un ejercicio"
        lines.append(f"- **Día {index + 1} · {current:%d/%m/%Y}:** {activity}")
    theory = max(10, round(total_minutes * .25))
    practice = max(5, total_minutes - theory)
    lines.extend([
        "", "## Método recomendado", "",
        f"- **{theory} minutos:** comprender el concepto y leer tus apuntes.",
        f"- **{practice} minutos:** escribir, corregir y explicar tu propio código.",
        "- Al terminar cada sesión: registra una duda y una cosa que ya puedes hacer.",
        "- Al finalizar: crea o mejora un mini proyecto relacionado con tu objetivo.",
        "", "*La ruta es orientativa: ajusta las sesiones a tu ritmo.*",
    ])
    return "\n".join(lines)


def demo_exam(topic: str, count: int) -> str:
    """Retos genéricos declarados como plantilla, sin fingir generación de IA."""
    topic = topic.strip() or "el tema elegido"
    templates = [
        f"Explica {topic} con tus palabras y escribe un ejemplo sencillo.",
        f"Escribe un programa breve que utilice {topic}.",
        f"Detecta tres errores comunes al usar {topic}.",
        f"Compara dos formas de resolver un problema usando {topic}.",
        f"Propón una pequeña función o consulta que demuestre {topic}.",
    ]
    lines = ["# Retos orientativos · modo demostración", "", "Esta es una plantilla local; para retos personalizados usa Gemini u Ollama.", ""]
    for i in range(count):
        lines.append(f"{i+1}. {templates[i % len(templates)]}")
    lines.extend(["", "**Consejo:** intenta cada reto antes de consultar una solución."])
    return "\n".join(lines)

"""CampusIA CodeMentor · Aprende lenguajes de programación con un mentor IA.

Iniciar: python -m streamlit run app.py
La aplicación mantiene apuntes y conversaciones solo en la sesión de Streamlit.
"""
from html import escape
from pathlib import Path

import streamlit as st

from campusia.agent import UniversityAgent
from campusia.config import CONFIG
from campusia.documents import load_example_chunks, read_document
from campusia.learning_catalog import LANGUAGES, roadmap_topics, starter_code
from campusia.models import StudentProfile
from campusia.providers import DemoProvider, GeminiProvider, OllamaProvider, ProviderError
from campusia.tools import build_learning_plan

st.set_page_config(page_title="CampusIA CodeMentor · Aprende a programar", page_icon="💻",
                   layout="wide", initial_sidebar_state="expanded")
st.markdown("<style>" + (Path(__file__).parent / "assets" / "styles.css").read_text(encoding="utf-8") + "</style>",
            unsafe_allow_html=True)

# Estado de la sesión: cada lenguaje conserva su propio chat y sus apuntes.
for key, initial in (
    ("conversations", {}), ("material_by_language", {}), ("plans_by_language", {}),
    ("challenge_by_language", {}), ("code_review_by_language", {}),
):
    if key not in st.session_state:
        st.session_state[key] = initial


def safe_run(operation):
    """Muestra un error entendible sin rastros de pila o datos confidenciales."""
    try:
        return operation()
    except (ValueError, ProviderError) as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(f"No se completó la operación ({type(exc).__name__}). Revisa tus archivos o la conexión.")
    return None


def model_provider():
    """Crea el adaptador cuando el usuario realiza una consulta."""
    selected = st.session_state.provider_mode
    if selected == "🧪 Demostración":
        return DemoProvider()
    if selected == "☁️ Gemini":
        return GeminiProvider(
            st.session_state.get("gemini_key_input", "") or CONFIG.gemini_key,
            st.session_state.get("gemini_model_input", CONFIG.gemini_model),
        )
    return OllamaProvider(st.session_state.get("ollama_model_input", CONFIG.ollama_model),
                          CONFIG.ollama_host)


def check_connection() -> None:
    """Comprueba el servicio elegido sin exponer la clave ni modificar la sesión."""
    try:
        if st.session_state.provider_mode == "🧪 Demostración":
            st.info("Modo local disponible. Para respuestas originales selecciona un modelo.")
        elif st.session_state.provider_mode == "☁️ Gemini":
            model_provider().generate("Responde en español con una sola frase.",
                                      "Confirma que el modelo responde.")
            st.success("Gemini respondió. Puedes comenzar a conversar.")
        else:
            from ollama import Client
            client = Client(host=CONFIG.ollama_host, timeout=15.0, trust_env=False)
            result = client.list()
            models = [getattr(m, "model", "") or getattr(m, "name", "") for m in result.models]
            selected = st.session_state.get("ollama_model_input", CONFIG.ollama_model).strip()
            if selected in models:
                st.success(f"Ollama accesible en {CONFIG.ollama_host}. Modelo: {selected}.")
            else:
                st.warning("Ollama responde, pero el modelo elegido no aparece instalado.")
                if models:
                    st.caption("Disponibles: " + ", ".join(models[:12]))
    except (ProviderError, ValueError) as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(f"No se conectó al servicio local ({type(exc).__name__}). "
                 f"Verifica {CONFIG.ollama_host} y el modelo instalado.")


def get_profile() -> StudentProfile:
    return StudentProfile(
        language=st.session_state.language,
        level=st.session_state.level,
        goal=st.session_state.goal.strip() or "Crear un mini proyecto",
        learning_style=st.session_state.learning_style,
    )


def page_header(kicker: str, title: str, description: str, tags: tuple[str, ...] = ()) -> None:
    """Cabecera editorial coherente; el contenido del usuario va escapado."""
    tags_html = "".join(f'<span class="chip">{escape(tag)}</span>' for tag in tags)
    st.markdown(
        f'<div class="header-surface"><div class="hero-topline">{escape(kicker)}</div>'
        f'<h1>{escape(title)}</h1><p>{escape(description)}</p>'
        f'<div class="chips">{tags_html}</div></div>', unsafe_allow_html=True,
    )


def show_sources(sources: list[str]) -> None:
    if sources:
        with st.expander(f"Material consultado · {len(sources)} referencia(s)"):
            for source in sources:
                st.caption("• " + source)


with st.sidebar:
    st.markdown('<div class="brand-name"><span class="brand-mark">⌘</span>CampusIA</div>'
                '<div class="brand-subtitle">CodeMentor · Tu espacio para aprender</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sep"></div>', unsafe_allow_html=True)
    st.caption("NAVEGACIÓN")
    page = st.radio("Sección", ["💬 Chat con mentor", "📚 Material de estudio",
                                    "🗓️ Mi plan de aprendizaje", "🧩 Práctica de código"],
                    label_visibility="collapsed", key="current_page")
    st.markdown('<div class="sidebar-sep"></div>', unsafe_allow_html=True)
    st.caption("TU APRENDIZAJE")
    st.selectbox("Lenguaje", LANGUAGES, key="language")
    st.selectbox("Nivel", ["Principiante", "Intermedio", "Avanzado"], key="level")
    st.text_input("¿Qué quieres conseguir?", value="Crear mi primer proyecto", key="goal")
    st.selectbox("Estilo del mentor", ["Paso a paso y con ejemplos", "Con ejercicios prácticos",
                                          "Explicaciones breves", "Con analogías simples"],
                 key="learning_style")
    st.markdown('<div class="sidebar-sep"></div>', unsafe_allow_html=True)
    with st.expander("⚙️ Motor de inteligencia artificial", expanded=True):
        st.radio("Proveedor", ["💻 Ollama local", "☁️ Gemini", "🧪 Demostración"], key="provider_mode")
        if st.session_state.provider_mode == "💻 Ollama local":
            st.text_input("Modelo instalado", value=CONFIG.ollama_model, key="ollama_model_input")
            st.caption("Funciona desde tu equipo con Ollama abierto.")
        elif st.session_state.provider_mode == "☁️ Gemini":
            st.text_input("Clave de API", key="gemini_key_input", type="password",
                          placeholder="Pega aquí tu clave")
            st.text_input("Modelo Gemini", value=CONFIG.gemini_model, key="gemini_model_input")
            st.caption("La consulta y los fragmentos recuperados se envían a Google.")
        else:
            st.caption("Sin IA generativa. Muestra planes y materiales de ejemplo.")
        if st.button("Comprobar conexión", use_container_width=True):
            check_connection()
    st.caption("UMSS · Proyecto educativo · No compartas credenciales")

profile = get_profile()
language = profile.language
history = st.session_state.conversations.setdefault(language, [])
materials = st.session_state.material_by_language.setdefault(language, [])

if page == "💬 Chat con mentor":
    page_header("MENTOR DE PROGRAMACIÓN", "Aprende programando, no memorizando.",
                "Pregunta, practica, equivócate y comprende cada concepto con tu mentor.",
                (language, profile.level, "Tus apuntes disponibles" if materials else "Listo para practicar"))
    head_a, head_b = st.columns([3, 1], vertical_alignment="center")
    with head_a:
        st.markdown("**Conversación**")
        st.caption(f"Mentor de {language}  ·  {st.session_state.provider_mode}")
    with head_b:
        if st.button("Nueva conversación", icon="🔄", use_container_width=True):
            st.session_state.conversations[language] = []
            st.rerun()

    suggested = (
        f"Enséñame las variables en {language} con un ejemplo sencillo",
        f"Dame un reto fácil de {language}, pero sin mostrar la solución",
        f"Explícame cómo crear un mini proyecto en {language}",
    )
    if not history:
        st.markdown('<div class="section-label">¿Por dónde empezamos?</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for idx, (column, text) in enumerate(zip(cols, suggested)):
            with column:
                if st.button(("Concepto básico", "Un reto práctico", "Un mini proyecto")[idx],
                             key=f"quick_{idx}", use_container_width=True):
                    st.session_state.pending_message = text

    # Contenedor desplazable para que los mensajes parezcan una conversación real.
    with st.container(height=470, border=False):
        if not history:
            with st.chat_message("assistant", avatar="💻"):
                st.markdown(
                    f"¡Hola! Soy **CodeMentor**. Vamos a aprender **{language}** a tu ritmo. "
                    "Puedes pedirme ejemplos, explicaciones, retos, pistas o revisión de código. "
                    "Si cargas apuntes, también podré utilizarlos como material de referencia."
                )
        else:
            for item in history:
                role = item["role"]
                with st.chat_message(role, avatar="🧑‍🎓" if role == "user" else "💻"):
                    st.markdown(item["content"])
                    if role == "assistant":
                        show_sources(item.get("sources", []))

    question = st.chat_input(f"Escribe tu pregunta sobre {language}…")
    question = question or st.session_state.pop("pending_message", "")
    if question:
        prior = [{"role": item["role"], "content": item["content"]} for item in history[-8:]]
        with st.spinner("CodeMentor está preparando tu respuesta..."):
            result = safe_run(lambda: UniversityAgent(model_provider()).chat(
                question, profile, materials, prior))
        if result:
            history.extend([
                {"role": "user", "content": question},
                {"role": "assistant", "content": result.text, "sources": result.sources},
            ])
            st.rerun()

    if history:
        transcript = "\n\n".join(
            f"## {'Estudiante' if item['role'] == 'user' else 'CodeMentor'}\n\n{item['content']}"
            for item in history
        )
        st.download_button("Guardar conversación", data=transcript,
                           file_name=f"chat_{language.lower().replace(' ', '_')}.md",
                           mime="text/markdown", use_container_width=False)
    st.caption("Las respuestas de la IA pueden equivocarse. Prueba el código en tu propio editor.")

elif page == "📚 Material de estudio":
    page_header("TU BIBLIOTECA", "Aprende a partir de tus apuntes.",
                "Sube material de clase y úsalo como referencia cuando converses con el mentor.",
                (language, "PDF · DOCX · TXT · MD", "Búsqueda local de fragmentos"))
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cargar material de ejemplo", use_container_width=True):
            st.session_state.material_by_language[language] = load_example_chunks(language)
            st.success(f"Material de muestra de {language} cargado.")
            st.rerun()
    with c2:
        if st.button("Quitar material de este lenguaje", use_container_width=True):
            st.session_state.material_by_language[language] = []
            st.rerun()
    uploaded = st.file_uploader("Selecciona hasta 6 documentos (máximo 8 MB cada uno)",
                                type=["pdf", "docx", "txt", "md"], accept_multiple_files=True)
    if st.button("Añadir documentos", type="primary", use_container_width=True):
        if not uploaded:
            st.warning("Selecciona al menos un archivo.")
        elif len(uploaded) > CONFIG.max_docs:
            st.warning(f"Se admiten hasta {CONFIG.max_docs} archivos por carga.")
        else:
            collected = []
            for file in uploaded:
                try:
                    collected.extend(read_document(file.name, file.getvalue(), CONFIG.max_file_mb))
                except Exception as exc:
                    st.warning(f"No se pudo leer {file.name}: {exc}")
            if collected:
                st.session_state.material_by_language[language] = collected
                st.success("Material procesado. Vuelve al chat y pregunta usando tus apuntes.")
    materials = st.session_state.material_by_language[language]
    if materials:
        st.markdown("#### Material activo")
        st.metric("Fragmentos disponibles", len(materials))
        for name in sorted({chunk.source for chunk in materials}):
            st.markdown(f"📄 **{name}**")
        with st.expander("Ver fragmento de muestra"):
            st.caption(materials[0].label)
            st.write(materials[0].text[:1400])
        st.info("El mentor consulta fragmentos relevantes de estos documentos al responder.")
    else:
        st.info("Todavía no hay material cargado. Prueba con los apuntes de ejemplo.")
    st.caption("Los archivos quedan en la sesión del servidor. Si utilizas Gemini, el material recuperado se envía a Google. No subas información privada.")

elif page == "🗓️ Mi plan de aprendizaje":
    page_header("TU HOJA DE RUTA", f"Tu camino para aprender {language}.",
                "Una ruta realista de teoría, práctica y mini proyectos, adaptada a tus horarios.",
                (language, profile.level, "Plan descargable"))
    st.markdown("#### Crea tu plan")
    st.caption("Puedes modificar los temas sugeridos antes de generarlo.")
    with st.form("learning_plan_form"):
        topics = st.text_area("Temas para estudiar (separados por comas)",
                              value=", ".join(roadmap_topics(language)),
                              height=100, key=f"plan_topics_{language}")
        col1, col2 = st.columns(2)
        with col1:
            days = st.select_slider("Duración de la ruta", options=[7, 14, 21, 30], value=14)
        with col2:
            hours = st.slider("Horas de práctica al día", min_value=.5, max_value=4.0,
                              value=1.5, step=.5)
        submit = st.form_submit_button("Crear plan de aprendizaje", type="primary", use_container_width=True)
    if submit:
        plan = safe_run(lambda: build_learning_plan(language, topics, days, hours, profile.goal))
        if plan:
            st.session_state.plans_by_language[language] = plan
    if language in st.session_state.plans_by_language:
        st.markdown("#### Tu plan personalizado")
        st.markdown(st.session_state.plans_by_language[language])
        st.download_button("Descargar plan (.md)", st.session_state.plans_by_language[language],
                           file_name=f"ruta_{language.lower().replace(' ', '_')}.md", mime="text/markdown")
    else:
        st.info("Selecciona cuánto tiempo estudiarás y genera tu primera ruta.")

else:  # Práctica de código
    page_header("APRENDER HACIENDO", f"Practica {language} con propósito.",
                "Resuelve desafíos y revisa fragmentos de código sin ejecutarlos en el servidor.",
                (language, "Retos guiados", "Revisión educativa"))
    tab_code, tab_challenge = st.tabs(["Revisar mi código", "Generar retos"])
    with tab_code:
        st.caption("El análisis sintáctico local funciona para Python. En otros lenguajes, el mentor comenta tu código con IA, sin compilarlo.")
        code = st.text_area(f"Código de {language}", value=starter_code(language),
                            height=240, key=f"code_{language}")
        if st.button("Analizar código", type="primary", use_container_width=True):
            with st.spinner("Revisando tu código..."):
                result = safe_run(lambda: UniversityAgent(model_provider()).code_help(code, profile))
            if result:
                st.session_state.code_review_by_language[language] = result
        result = st.session_state.code_review_by_language.get(language)
        if result:
            st.markdown("#### Explicación del mentor")
            st.markdown(result.text)
    with tab_challenge:
        with st.form("challenge_form"):
            topic = st.text_input("Tema que quieres practicar", value=roadmap_topics(language)[2])
            n = st.slider("Número de retos", 2, 8, 4)
            submitted = st.form_submit_button("Generar retos", type="primary", use_container_width=True)
        if submitted:
            with st.spinner("Preparando desafíos progresivos..."):
                result = safe_run(lambda: UniversityAgent(model_provider()).exam(
                    topic, n, profile, materials))
            if result:
                st.session_state.challenge_by_language[language] = result
        result = st.session_state.challenge_by_language.get(language)
        if result:
            st.markdown(result.text)
            show_sources(result.sources)
            st.download_button("Guardar retos (.md)", result.text,
                               file_name=f"retos_{language.lower().replace(' ', '_')}.md",
                               mime="text/markdown")

st.markdown('<div class="sidebar-sep"></div>', unsafe_allow_html=True)
st.caption("CampusIA CodeMentor · Taller universitario · Aprende, practica y construye · 2026")

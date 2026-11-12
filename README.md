# CampusIA CodeMentor — Aprende lenguajes de programación

Aplicación educativa profesional hecha en **Python + Streamlit**, preparada para el taller «Crea tu propio asistente de IA para la universidad» de la UMSS.

**Objetivo:** que cada estudiante cree su propio espacio para aprender un lenguaje de programación, conversar con un mentor de IA, practicar código, consultar apuntes y seguir un plan de aprendizaje.

## Funciones de esta versión

| Sección | Qué puedes hacer |
|---|---|
| **Chat con mentor** | Conversaciones tipo mensajería, burbujas diferenciadas, memoria limitada de mensajes, preguntas rápidas y exportación Markdown; un historial por lenguaje |
| **Material de estudio** | Subir PDF, DOCX, TXT o MD (máx. seis archivos de 8 MB por carga); recuperación léxica de fragmentos con etiquetas de fuente |
| **Mi plan de aprendizaje** | Rutas de 7, 14, 21 y 30 días, con temas por lenguaje, práctica y mini proyecto; funciona sin IA |
| **Práctica de código** | Generar retos adaptados a un lenguaje; solicitar revisión de código por IA; verificación sintáctica local únicamente para Python |
| **Motores** | Ollama local, Gemini API o demostración sin IA generativa |

**Se eliminaron por completo el promedio de notas y las secciones de materias no relacionadas con aprender lenguajes de programación.**

### Lenguajes

Python, JavaScript, TypeScript, Java, C++, C#, SQL, Go, Kotlin y Rust. Se incluye una opción abierta para otros lenguajes.

## Instalación en Windows 11

1. Descomprime el ZIP.
2. En la carpeta principal ejecuta `instalar.bat` (recomendado: Python 3.11 o superior).
3. Ejecuta `iniciar.bat`.
4. Abre **http://localhost:8501** en tu navegador.

Instalación manual en PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Conectar Ollama (recomendado en la computadora de la instructora)

Como ya tienes `qwen3:4b` instalado, **no lo vuelvas a descargar**. Comprueba que Ollama esté levantado:

```powershell
ollama list
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

En el panel lateral selecciona **Ollama local** y modelo `qwen3:4b`. Haz clic en **Comprobar conexión**. Si `ollama serve` dice que el puerto 11434 está ocupado pero el segundo comando devuelve modelos, probablemente Ollama ya se está ejecutando y no debes iniciar otro servidor.

**Diferencia importante:** la variable de entorno `OLLAMA_HOST` puede definir la dirección de escucha del servidor (`0.0.0.0:11434`), pero CampusIA usa la URL independiente `CAMPUSIA_OLLAMA_URL=http://127.0.0.1:11434` como cliente.

## Conectar Gemini

1. Crea tu propia clave en [Google AI Studio](https://aistudio.google.com/apikey).
2. Selecciona **Gemini** en el panel lateral.
3. Pega tu clave (no la compartas ni la subas a GitHub).
4. Introduce **un nombre de modelo habilitado en tu proyecto de Google AI Studio** (el valor inicial se puede editar).
5. Pulsa **Comprobar conexión**.

Los errores `503 UNAVAILABLE` suelen señalar saturación temporal del proveedor; prueba de nuevo más tarde o cambia a otro modelo habilitado. El `404` puede indicar que el modelo elegido no está disponible en tu cuenta. El `429` suele indicar un límite de cuota. Las condiciones y cuotas cambian según región y cuenta.

Puedes configurar la clave en un `.env` local copiando `.env.example`, pero **no es necesario**; también funciona desde el panel lateral. Nunca incluyas claves en archivos compartidos.

## Demostración sugerida de 5 minutos

1. Elige **JavaScript** y nivel Principiante. Pulsa «Concepto básico» en el chat.
2. Carga `apuntes_javascript.txt` desde **Material de estudio** y pregunta «¿Qué diferencia hay entre let y const?». Abre **Material consultado** para verificar la fuente.
3. En **Práctica de código**, solicita 3 retos de funciones JavaScript.
4. En **Mi plan de aprendizaje**, genera una ruta de 14 días y descárgala.
5. Cambia a **Python** para mostrar otro chat e inspeccionar un error de sintaxis sin ejecutar el código.

## Arquitectura

```text
CampusIA_CodeMentor_Profesional/
├── app.py                         # Interfaz de mensajería y navegación
├── assets/styles.css              # Estilo oscuro profesional y responsive
├── campusia/
│   ├── agent.py                   # Coordinación de mentor, recuperación y retos
│   ├── config.py                  # Configuración segura, URL Ollama cliente
│   ├── documents.py               # Lectura PDF/Word/TXT/MD y BM25
│   ├── learning_catalog.py        # Lenguajes, rutas y código inicial
│   ├── models.py                  # Contratos tipados
│   ├── prompts.py                 # Instrucciones didácticas del agente
│   ├── providers.py               # Ollama, Gemini, demo
│   └── tools.py                   # Plan de aprendizaje y parser Python
├── ejemplos/                      # Material ficticio de programación
├── tests/                         # Pruebas automatizadas
├── docs/                          # Arquitectura y checklist técnico
├── instalar.bat / iniciar.bat
└── requirements.txt
```

La búsqueda en apuntes es **BM25 basada en palabras**, no embeddings; al combinar recuperación y generación del LLM se obtiene un RAG introductorio. El asistente está **guiado por herramientas**, no es un agente autónomo de propósito general.

## Verificación antes del taller

```powershell
.\.venv\Scripts\python.exe verificar.py
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Las pruebas sin acceso a proveedores verifican reglas, documentos, planes y orquestación. **La conexión real a Gemini y Ollama debe probarse en el equipo donde se presentará.**

## Privacidad y limitaciones

- Los apuntes y el historial viven en la memoria de sesión del servidor; no se guardan automáticamente en una base de datos. Guarda manualmente lo que quieras conservar.
- El material recuperado se envía a Google cuando usas Gemini; con Ollama se procesa en el equipo donde se ejecuta Ollama.
- Solo Python cuenta con revisión estática de sintaxis mediante `ast.parse` (no ejecuta código). Otros lenguajes reciben análisis orientativo de la IA, no una compilación real.
- La IA puede cometer errores; prueba los ejemplos en tu IDE y consulta documentación oficial.
- No hay login ni controles de acceso de producción. No publiques la app sin añadir autenticación y medidas de seguridad.
- No incluye OCR; un PDF escaneado sin texto reconocible no se podrá leer.

Documentación oficial: [Streamlit Chat](https://docs.streamlit.io/develop/api-reference/chat), [Gemini Python SDK](https://googleapis.github.io/python-genai/), [Ollama Python](https://github.com/ollama/ollama-python).

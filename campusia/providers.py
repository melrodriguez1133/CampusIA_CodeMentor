"""Adaptadores LLM intercambiables: Gemini, Ollama y demostración.

El modo demostración es deliberadamente NO generativo; sigue siendo útil
para mostrar recuperación de apuntes y herramientas locales sin API key.
"""
from abc import ABC, abstractmethod
from typing import Sequence


class ProviderError(RuntimeError):
    """Error de conexión o servicio mostrado con un mensaje útil."""


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def generate(self, system: str, user: str,
                 history: Sequence[dict[str, str]] = ()) -> str:
        """Devuelve texto generado, o lanza ProviderError."""


class DemoProvider(LLMProvider):
    name = "Demostración (sin modelo)"

    def generate(self, system: str, user: str,
                 history: Sequence[dict[str, str]] = ()) -> str:
        del system, history
        if "[FUENTE" in user:
            # Las fuentes son manejadas por el agente; sin IA no interpretamos
            # ni pretendemos comprender semánticamente el contenido.
            return (
                "**Demostración de búsqueda en apuntes:** localicé fragmentos "
                "relacionados con tu consulta; revísalos en **Material consultado**. "
                "Para una explicación redactada usando esos fragmentos, "
                "activa un modelo (Gemini u Ollama)."
            )
        return (
            "**Modo demostración activo.** Puedes cargar apuntes, localizar "
            "fragmentos, verificar sintaxis Python y crear un "
            "plan de estudio sin conectar un modelo. Para explicaciones "
            "originales y retos personalizados, selecciona "
            "**Gemini** u **Ollama** en la barra lateral."
        )


class GeminiProvider(LLMProvider):
    name = "Gemini"

    def __init__(self, api_key: str, model: str) -> None:
        if not api_key.strip():
            raise ProviderError("Falta GEMINI_API_KEY. Pégala en el panel o configúrala en .env.")
        self.api_key = api_key.strip()
        self.model = model.strip() or "gemini-3.8-flash"

    def generate(self, system: str, user: str,
                 history: Sequence[dict[str, str]] = ()) -> str:
        try:
            from google import genai
            from google.genai import types
            with genai.Client(api_key=self.api_key) as client:
                contents = []
                for entry in list(history)[-8:]:
                    role = "model" if entry.get("role") == "assistant" else "user"
                    contents.append(types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=entry.get("content", "")[:2800])],
                    ))
                contents.append(types.Content(
                    role="user", parts=[types.Part.from_text(text=user[:18000])],
                ))
                response = client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system,
                        # Gemini 3.8 ya no acepta temperature/top_p/top_k.
                        max_output_tokens=3000,
                    ),
                )
                answer = response.text or ""
                if not answer.strip():
                    raise ProviderError("Gemini no devolvió texto. Revisa filtros, cuota o modelo.")
                return answer
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError(
                "No se pudo consultar Gemini. Verifica conexión, API key, nombre del "
                f"modelo y límites de cuota. Detalle técnico: {type(exc).__name__}: {str(exc)[:210]}"
            ) from exc


class OllamaProvider(LLMProvider):
    name = "Ollama local"

    def __init__(self, model: str, host: str) -> None:
        self.model = model.strip() or "qwen3:4b"
        self.host = host.strip() or "http://127.0.0.1:11434"

    def generate(self, system: str, user: str,
                 history: Sequence[dict[str, str]] = ()) -> str:
        try:
            from ollama import Client
            client = Client(host=self.host, timeout=120.0, trust_env=False)
            messages = [{"role": "system", "content": system}]
            for entry in list(history)[-8:]:
                messages.append({
                    "role": "assistant" if entry.get("role") == "assistant" else "user",
                    "content": entry.get("content", "")[:2800],
                })
            messages.append({"role": "user", "content": user[:18000]})
            response = client.chat(
                model=self.model,
                messages=messages,
                options={"temperature": 0.35, "num_predict": 1900},
            )
            answer = response.message.content or ""
            if not answer.strip():
                raise ProviderError("Ollama devolvió una respuesta vacía.")
            return answer
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError(
                "No se pudo consultar Ollama. Verifica el servidor, el puerto y el modelo. "
                f"Ejecuta: ollama list y consulta {self.host}/api/tags. "
                f"Detalle: {type(exc).__name__}: {str(exc)[:180]}"
            ) from exc

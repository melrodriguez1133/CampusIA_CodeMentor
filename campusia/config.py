"""Configuración de CampusIA sin claves incrustadas.

Importante: OLLAMA_HOST se utiliza por Ollama para definir la dirección
EN LA QUE ESCUCHA su servidor (puede ser 0.0.0.0). No debe reutilizarse
como destino del cliente HTTP de CampusIA. Para el cliente se usa una
variable independiente: CAMPUSIA_OLLAMA_URL.
"""

import os
from dataclasses import dataclass, field
from urllib.parse import urlsplit

from dotenv import load_dotenv

load_dotenv()


def _ollama_client_url() -> str:
    """Devuelve una URL alcanzable para el cliente local de Ollama.

    Nunca se toma OLLAMA_HOST: una configuración de escucha como
    0.0.0.0:11434 puede ser válida para el servidor, pero no es el
    destino apropiado para las solicitudes desde CampusIA.
    """
    raw = os.getenv("CAMPUSIA_OLLAMA_URL", "http://127.0.0.1:11434").strip()
    if not raw:
        raw = "http://127.0.0.1:11434"
    if "://" not in raw:
        raw = "http://" + raw

    parsed = urlsplit(raw)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("CAMPUSIA_OLLAMA_URL debe ser una URL HTTP válida.")

    host = parsed.hostname
    if host in ("0.0.0.0", "::", "[::]"):
        host = "127.0.0.1"

    # Evita rutas y credenciales innecesarias; ollama.Client espera la base URL.
    port = f":{parsed.port}" if parsed.port is not None else ""
    if ":" in host:  # compatibilidad con IPv6
        host = f"[{host}]"
    return f"{parsed.scheme}://{host}{port}"


@dataclass(frozen=True)
class AppConfig:
    """Valores predeterminados; .env puede sobreescribirlos."""

    gemini_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    gemini_model: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-3.8-flash"))
    ollama_model: str = field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "qwen3:4b"))
    ollama_host: str = field(default_factory=_ollama_client_url)
    max_docs: int = 6
    max_file_mb: int = 8


CONFIG = AppConfig()

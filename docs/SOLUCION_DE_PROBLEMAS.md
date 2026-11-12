# Solución de problemas · CampusIA CodeMentor

## El servidor Ollama responde en PowerShell, pero CampusIA no conecta

1. Confirma que `Invoke-RestMethod http://127.0.0.1:11434/api/tags` muestra los modelos.
2. Si sí responde, **no ejecutes otra vez** `ollama serve` (el puerto puede estar ocupado por el servidor en marcha).
3. En `.env` usa `CAMPUSIA_OLLAMA_URL=http://127.0.0.1:11434` o elimina el valor para usar el predeterminado.
4. Evita configurar el destino del cliente como `0.0.0.0:11434`; esa es una dirección de escucha.
5. Reinicia Streamlit y comprueba que el modelo escrito existe (`ollama list`).

## Gemini devuelve 503, 404 o 429

- **503:** el modelo puede estar temporalmente saturado. Reintenta después o utiliza Ollama.
- **404:** comprueba el ID del modelo y que esté habilitado para tu API key.
- **429:** revisa cuota y límites de uso de tu proyecto.
- Nunca expongas la clave en capturas ni repositorios. Puedes escribir otro modelo autorizado en la barra lateral.

## El chat no responde como IA

- Asegúrate de no estar en **Demostración**: ese modo no genera explicaciones originales.
- Comprueba el modelo con el botón del panel lateral.

## No aparecen fuentes

- Primero carga material en la sección del lenguaje actual.
- La recuperación es léxica BM25: usa palabras clave que sí estén en los documentos.
- Los PDF escaneados no se leen si carecen de capa de texto.

## No funciona la revisión de sintaxis de JavaScript / Java / SQL

- Es intencional: `ast.parse()` solo valida sintaxis **Python**.
- Para otros lenguajes, selecciona Gemini u Ollama y obtén sugerencias **orientativas** sin ejecutar el programa.

## El estilo se ve viejo

- Verifica que existe `assets/styles.css` junto a `app.py`.
- Fuerza actualización del navegador con `Ctrl + F5`.
- Reinicia Streamlit con `Ctrl + C` y `iniciar.bat`.

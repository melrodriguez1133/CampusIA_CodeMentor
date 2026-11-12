"""Catálogo pedagógico; no depende de una API de inteligencia artificial."""

LANGUAGES: tuple[str, ...] = (
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#",
    "SQL", "Go", "Kotlin", "Rust", "Otro lenguaje",
)

ROADMAP: dict[str, tuple[str, ...]] = {
    "Python": ("Sintaxis y variables", "Tipos y operadores", "Condicionales y bucles", "Funciones", "Listas y diccionarios", "Archivos y mini proyecto"),
    "JavaScript": ("let, const y tipos", "Condiciones y bucles", "Funciones y arrow functions", "Arrays y objetos", "DOM y eventos", "fetch, promesas y mini proyecto"),
    "TypeScript": ("Sintaxis de JavaScript", "Tipos primitivos y uniones", "Interfaces y tipos", "Funciones tipadas", "Genéricos y módulos", "Proyecto pequeño tipado"),
    "Java": ("Tipos y variables", "Condicionales y bucles", "Clases y objetos", "Métodos y encapsulación", "Colecciones y excepciones", "Mini proyecto de consola"),
    "C++": ("Sintaxis, variables y tipos", "Control de flujo", "Funciones y referencias", "Vectores y cadenas", "Clases y objetos", "Gestión de memoria y mini proyecto"),
    "C#": ("Tipos y variables", "Control de flujo", "Métodos", "Clases y objetos", "Colecciones y LINQ", "Mini proyecto .NET"),
    "SQL": ("SELECT, FROM y WHERE", "ORDER BY y LIMIT", "JOIN entre tablas", "GROUP BY y agregaciones", "INSERT, UPDATE y DELETE", "Subconsultas y mini proyecto"),
    "Go": ("Variables y tipos", "Control de flujo", "Funciones", "Slices y maps", "Structs e interfaces", "Errores y mini proyecto"),
    "Kotlin": ("Variables y tipos", "Null safety", "Condicionales y colecciones", "Funciones", "Clases y data classes", "Corrutinas y mini proyecto"),
    "Rust": ("Variables y mutabilidad", "Tipos y control de flujo", "Ownership y borrowing", "Funciones y structs", "Enums y manejo de errores", "Colecciones y mini proyecto"),
}

STARTER_CODES: dict[str, str] = {
    "Python": 'def saludar(nombre):\n    return f"Hola, {nombre}"\n\nprint(saludar("UMSS"))',
    "JavaScript": 'function saludar(nombre) {\n  return `Hola, ${nombre}`;\n}\nconsole.log(saludar("UMSS"));',
    "TypeScript": 'function saludar(nombre: string): string {\n  return `Hola, ${nombre}`;\n}\nconsole.log(saludar("UMSS"));',
    "Java": 'public class Main {\n  public static void main(String[] args) {\n    System.out.println("Hola UMSS");\n  }\n}',
    "C++": '#include <iostream>\nint main() {\n  std::cout << "Hola UMSS\\n";\n  return 0;\n}',
    "C#": 'using System;\nConsole.WriteLine("Hola UMSS");',
    "SQL": 'SELECT nombre, carrera\nFROM estudiantes\nWHERE carrera = \'Sistemas\';',
    "Go": 'package main\nimport "fmt"\nfunc main() {\n    fmt.Println("Hola UMSS")\n}',
    "Kotlin": 'fun main() {\n    println("Hola UMSS")\n}',
    "Rust": 'fn main() {\n    println!("Hola UMSS");\n}',
}


def roadmap_topics(language: str) -> tuple[str, ...]:
    """Temario base orientativo para un lenguaje elegido por el estudiante."""
    return ROADMAP.get(language, (
        "Instalación y primer programa", "Variables y tipos", "Control de flujo",
        "Funciones", "Colecciones", "Mini proyecto final",
    ))


def starter_code(language: str) -> str:
    """Ejemplo editable para empezar a aprender, nunca se ejecuta en el servidor."""
    return STARTER_CODES.get(language, "// Pega aquí tu código y solicita una explicación.")

from pathlib import Path
import re
import sys


REQUIRED_SECTIONS = (
    "## 1. Título y pitch",
    "## 2. Fuente de datos",
    "## 3. Preguntas de negocio",
    "## 4. Stack técnico",
    "## 5. Estructura del análisis",
    "## 6. Visualización final",
    "## 7. Frase para el portfolio",
    "## 8. Nivel de dificultad",
)


def validate_repository(root: Path) -> list[str]:
    errors: list[str] = []
    briefs = sorted((root / "projects").glob("*/README.md"))
    if len(briefs) != 5:
        errors.append(f"Expected 5 project briefs, found {len(briefs)}")

    main = (root / "README.md").read_text(encoding="utf-8")
    for brief in briefs:
        text = brief.read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            if section not in text:
                errors.append(f"{brief.parent.name}: missing {section}")
        relative = brief.relative_to(root).as_posix()
        if relative not in main:
            errors.append(f"README: missing link to {relative}")
        if not re.search(r"https://", text):
            errors.append(f"{brief.parent.name}: missing source URL")
    return errors


if __name__ == "__main__":
    problems = validate_repository(Path(__file__).resolve().parents[1])
    if problems:
        print("\n".join(problems))
        sys.exit(1)
    print("Portfolio validation passed.")

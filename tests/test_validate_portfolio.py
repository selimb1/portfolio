from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.validate_portfolio import validate_repository


SECTIONS = (
    "## 1. Título y pitch",
    "## 2. Fuente de datos",
    "## 3. Preguntas de negocio",
    "## 4. Stack técnico",
    "## 5. Estructura del análisis",
    "## 6. Visualización final",
    "## 7. Frase para el portfolio",
    "## 8. Nivel de dificultad",
)


class PortfolioValidationTest(unittest.TestCase):
    def build_repo(self, root: Path) -> None:
        links = []
        for index in range(1, 6):
            folder = root / "projects" / f"0{index}-project"
            folder.mkdir(parents=True)
            (folder / "README.md").write_text(
                "# Proyecto\n\n"
                + "\n\n".join(f"{section}\n\nContenido" for section in SECTIONS)
                + "\n\nhttps://example.com/source\n",
                encoding="utf-8",
            )
            links.append(f"[Proyecto {index}](projects/0{index}-project/README.md)")
        (root / "README.md").write_text(
            "# Portfolio\n\n" + "\n".join(links), encoding="utf-8"
        )

    def test_valid_repository_has_no_errors(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.build_repo(root)
            self.assertEqual(validate_repository(root), [])

    def test_missing_required_section_is_reported(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.build_repo(root)
            brief = root / "projects" / "03-project" / "README.md"
            content = brief.read_text(encoding="utf-8")
            brief.write_text(
                content.replace("## 3. Preguntas de negocio", "## Preguntas"),
                encoding="utf-8",
            )
            errors = validate_repository(root)
            self.assertTrue(any("03-project" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

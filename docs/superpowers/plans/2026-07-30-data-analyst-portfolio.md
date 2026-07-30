# Data Analyst Portfolio Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publicar una portada ejecutiva y cinco briefs reproducibles que presenten un perfil de analista de datos con criterio contable-financiero y de economía conductual.

**Architecture:** `README.md` funciona como índice y resumen de decisión; cada carpeta bajo `projects/` contiene un brief autónomo con una estructura contractual de ocho secciones. Un validador Python con biblioteca estándar comprueba cobertura, navegación, fuentes e integridad editorial.

**Tech Stack:** Markdown, Python 3 estándar, Git y GitHub.

---

### Task 1: Validador del contrato editorial

**Files:**
- Create: `tests/test_validate_portfolio.py`
- Create: `scripts/validate_portfolio.py`

- [ ] **Step 1: Write the failing test**

Crear `tests/test_validate_portfolio.py` con pruebas temporales que importen `validate_repository`, construyan cinco briefs válidos y comprueben que un brief sin “Preguntas de negocio” produce un error:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_validate_portfolio.py -v`

Expected: FAIL con `ModuleNotFoundError: No module named 'scripts.validate_portfolio'`.

- [ ] **Step 3: Write minimal implementation**

Crear `scripts/validate_portfolio.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_validate_portfolio.py -v`

Expected: dos pruebas en estado `ok`.

- [ ] **Step 5: Commit**

```bash
git add tests/test_validate_portfolio.py scripts/validate_portfolio.py
git commit -m "test: add portfolio content validator"
```

### Task 2: Portada ejecutiva

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Write the complete overview**

Reemplazar la línea inicial por:

- propuesta de valor de dos párrafos;
- tabla resumen con cinco filas y columnas de nivel, proyecto, problema, datos, stack y señal;
- enlaces a los cinco briefs;
- matriz de cobertura de criterios;
- guía de lectura y nota de honestidad analítica.

- [ ] **Step 2: Run the validator to observe missing briefs**

Run: `python3 scripts/validate_portfolio.py`

Expected: FAIL con “Expected 5 project briefs, found 0”.

- [ ] **Step 3: Check Markdown whitespace**

Run: `git diff --check -- README.md`

Expected: sin salida.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: add executive portfolio overview"
```

### Task 3: Proyectos financiero-contables y SQL a escala

**Files:**
- Create: `projects/01-working-capital/README.md`
- Create: `projects/02-complaint-risk-sql/README.md`

- [ ] **Step 1: Write Project 1**

Desarrollar “Rentabilidad no es caja” con SEC Financial Statement Data Sets, cohorte de empresas comparables, normalización XBRL, DSO/DIO/DPO, ciclo de conversión de caja, puente EBITDA-caja y small multiples. Incluir límites de comparabilidad y frase con campos `[X]`.

- [ ] **Step 2: Write Project 2**

Desarrollar “El costo oculto del reclamo” con CFPB Consumer Complaint Database. La capa analítica se implementará en SQL puro con staging, deduplicación, ventanas, cohortes, tasas de respuesta y segmentación operativa. Explicitar que no se deben comparar empresas sin denominador de clientes o exposición.

- [ ] **Step 3: Validate the two briefs**

Run: `python3 scripts/validate_portfolio.py`

Expected: FAIL únicamente porque todavía faltan tres briefs.

- [ ] **Step 4: Commit**

```bash
git add projects/01-working-capital/README.md projects/02-complaint-risk-sql/README.md
git commit -m "docs: add finance and SQL project briefs"
```

### Task 4: Economía conductual y modelo predictivo

**Files:**
- Create: `projects/03-behavioral-finance/README.md`
- Create: `projects/04-payment-risk/README.md`

- [ ] **Step 1: Write Project 3**

Desarrollar “La brecha entre saber y hacer” con la encuesta pública de bienestar financiero CFPB. Definir segmentos interpretables a partir de conductas, actitudes y resiliencia financiera; usar clustering solo como apoyo y validar estabilidad, utilidad y asociaciones con una regresión interpretable.

- [ ] **Step 2: Write Project 4**

Desarrollar “Cobrar antes de perseguir” con un generador sintético de facturas B2B. Especificar esquema, reglas de generación, corte temporal, variables disponibles al emitir la factura, regresión logística calibrada, costos de falsos positivos y negativos, y política de acción por bandas de riesgo.

- [ ] **Step 3: Validate the four briefs**

Run: `python3 scripts/validate_portfolio.py`

Expected: FAIL únicamente porque todavía falta el quinto brief.

- [ ] **Step 4: Commit**

```bash
git add projects/03-behavioral-finance/README.md projects/04-payment-risk/README.md
git commit -m "docs: add behavioral and predictive project briefs"
```

### Task 5: Sistema senior de anomalías y cierre editorial

**Files:**
- Create: `projects/05-spend-anomalies/README.md`

- [ ] **Step 1: Write Project 5**

Desarrollar “Cada peso deja una huella” con Checkbook NYC API. Combinar reglas contables, duplicados aproximados, concentración de proveedor, fraccionamiento, estacionalidad, ley de Benford como señal secundaria e Isolation Forest. Diseñar una cola de revisión explicable y aclarar que anomalía no equivale a fraude.

- [ ] **Step 2: Run all automated checks**

Run: `python3 -m unittest discover -s tests -v && python3 scripts/validate_portfolio.py && git diff --check`

Expected: dos pruebas `ok`, “Portfolio validation passed.” y sin errores de whitespace.

- [ ] **Step 3: Inspect navigation and requirement coverage**

Run:

```bash
for file in projects/*/README.md; do
  printf '%s ' "$file"
  rg -c '^## [1-8]\.' "$file"
done
```

Expected: cada archivo termina con `8`.

- [ ] **Step 4: Commit**

```bash
git add projects/05-spend-anomalies/README.md
git commit -m "docs: add senior spend anomaly project"
```

### Task 6: Publicación

**Files:**
- No additional files.

- [ ] **Step 1: Review intended diff**

Run: `git status -sb && git diff origin/main...HEAD --stat && git log --oneline origin/main..HEAD`

Expected: solo documentación, validador y pruebas del portfolio; `.codebase-memory/` permanece sin stage.

- [ ] **Step 2: Push branch**

Run: `git push -u origin agent/data-analyst-portfolio`

Expected: rama remota creada con seguimiento configurado.

- [ ] **Step 3: Open draft pull request**

Crear un PR hacia `main` que explique la narrativa, los cinco proyectos, las fuentes verificadas y los checks ejecutados.

- [ ] **Step 4: Report result**

Informar rama, commits, URL del PR, archivos principales y validaciones.

from __future__ import annotations

from pathlib import Path

import nbformat
from nbclient import NotebookClient

from portfolio_analytics.common import project_root


PROJECTS = [
    {
        "directory": "01-working-capital",
        "title": "Rentabilidad no es caja",
        "module": "working_capital",
        "decision": "¿Qué empresa está absorbiendo caja a través del capital de trabajo?",
        "conclusion": "Traducir días del ciclo de caja a dólares cambia la prioridad de intervención.",
    },
    {
        "directory": "02-complaint-risk-sql",
        "title": "El costo oculto del reclamo",
        "module": "complaint_sql",
        "decision": "¿Qué empresa debe entrar primero a una revisión operativa dentro de esta muestra?",
        "conclusion": "La cola combina volumen y respuesta tardía; no reemplaza un denominador de clientes.",
    },
    {
        "directory": "03-behavioral-finance",
        "title": "La brecha entre saber y hacer",
        "module": "behavioral_finance",
        "decision": "¿Qué fricción conductual debería orientar una intervención financiera?",
        "conclusion": "Los perfiles requieren acciones distintas; la asociación observada no demuestra causalidad.",
    },
    {
        "directory": "04-payment-risk",
        "title": "Cobrar antes de perseguir",
        "module": "payment_risk",
        "decision": "¿Cuánto riesgo captura un equipo que solo puede revisar el decil superior?",
        "conclusion": "Un modelo simple crea valor cuando respeta el tiempo y se traduce a capacidad operativa.",
    },
    {
        "directory": "05-spend-anomalies",
        "title": "Cada peso deja una huella",
        "module": "spend_anomalies",
        "decision": "¿Qué pagos maximizan exposición revisada y fuerza de evidencia?",
        "conclusion": "Una anomalía abre una revisión documental; nunca confirma fraude por sí sola.",
    },
]


def notebook_for(config: dict[str, str]) -> nbformat.NotebookNode:
    directory = config["directory"]
    module = config["module"]
    notebook = nbformat.v4.new_notebook(
        cells=[
            nbformat.v4.new_markdown_cell(
                f"# {config['title']}\n\n"
                f"**Decisión:** {config['decision']}\n\n"
                "Notebook ejecutado sobre la muestra versionada del repositorio."
            ),
            nbformat.v4.new_markdown_cell(
                "## 1. Contrato y calidad\n\n"
                "Se comprueba la trazabilidad de la fuente, el tamaño de la muestra y las métricas finitas."
            ),
            nbformat.v4.new_code_cell(
                "from pathlib import Path\n"
                "from IPython.display import Image, display\n"
                "from portfolio_analytics.common import project_root, read_json\n"
                "root = project_root()\n"
                f"project = root / 'projects/{directory}'\n"
                "source = read_json(project / 'data/source.json')\n"
                "display({'rows': source['rows'], 'source': source['url'], "
                "'retrieved_at': source['retrieved_at']})"
            ),
            nbformat.v4.new_markdown_cell(
                "## 2. Ejecución reproducible\n\n"
                "La siguiente celda vuelve a correr la lógica compartida por el script y las pruebas."
            ),
            nbformat.v4.new_code_cell(
                f"from portfolio_analytics.{module} import analyze\n"
                "metrics = analyze(project / 'data/sample.csv', project / 'outputs')\n"
                "display(metrics)"
            ),
            nbformat.v4.new_markdown_cell(
                "## 3. Resultado visual\n\n"
                "La figura se genera desde los mismos datos y queda versionada para revisión rápida."
            ),
            nbformat.v4.new_code_cell(
                "display(Image(filename=str(project / 'outputs/figure.png'), width=900))"
            ),
            nbformat.v4.new_markdown_cell(
                f"## 4. Conclusión y límite\n\n{config['conclusion']}"
            ),
        ],
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3"},
        },
    )
    identifier_prefix = directory.replace("-", "_")
    for index, cell in enumerate(notebook.cells, start=1):
        cell["id"] = f"{identifier_prefix}_{index:02d}"
    return notebook


def build_all(root: Path) -> None:
    for config in PROJECTS:
        notebook = notebook_for(config)
        destination = (
            root / "projects" / config["directory"] / "notebooks" / "analysis.ipynb"
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        client = NotebookClient(
            notebook,
            timeout=240,
            kernel_name="python3",
            resources={"metadata": {"path": str(root)}},
            record_timing=False,
        )
        executed = client.execute()
        nbformat.write(executed, destination)
        print(f"Built {destination.relative_to(root)}")


if __name__ == "__main__":
    build_all(project_root())

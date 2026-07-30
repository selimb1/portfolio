# Diseño de evidencia técnica ejecutable

## Objetivo

Elevar el portfolio desde briefs conceptuales a cinco casos ejecutables y verificables. Un recruiter debe poder observar, sin instalar nada, resultados cuantificados, figuras y decisiones; un hiring manager debe poder clonar el repositorio, ejecutar una orden y auditar datos, SQL, modelos y pruebas.

## Principio de entrega

Cada proyecto tendrá dos modos:

- **Demo offline:** usa una muestra versionada y produce resultados determinísticos en menos de dos minutos.
- **Refresh:** descarga o genera nuevamente la fuente documentada y reconstruye la muestra.

Los datos completos y archivos raw voluminosos no se versionan. Sí se versionan muestras pequeñas con metadatos de procedencia, outputs ejecutados y notebooks con resultados.

## Contrato técnico común

Cada carpeta de proyecto incluirá:

- `data/sample.csv`: muestra utilizable sin red;
- `data/source.json`: URL, fecha de extracción, alcance, licencia y transformaciones;
- `notebooks/analysis.ipynb`: notebook ejecutado de principio a fin;
- `outputs/metrics.json`: métricas principales legibles por máquina;
- `outputs/figure.png`: visual principal;
- `outputs/*.csv`: tablas que sustentan la figura y los hallazgos;
- `README.md`: hallazgos reales, reproducción, estructura y limitaciones.

El código reutilizable vivirá en `src/portfolio_analytics/`; el SQL del proyecto 2 vivirá en su carpeta para que pueda evaluarse sin navegar strings Python.

## Infraestructura del repositorio

- `pyproject.toml`: dependencias y configuración de pruebas.
- `Makefile`: `setup`, `data`, `analysis`, `notebooks`, `test` y `all`.
- `.github/workflows/ci.yml`: instalación, pruebas, validación editorial y ejecución offline.
- `scripts/bootstrap_data.py`: construcción de muestras desde fuentes públicas.
- `scripts/run_all.py`: ejecución de los cinco análisis.
- `scripts/build_notebooks.py`: notebooks estructurados y ejecutados.
- `scripts/validate_portfolio.py`: contrato editorial y técnico.
- `tests/`: pruebas unitarias, de datos y de integración liviana.

## Proyecto 1 — Capital de trabajo

Fuente: SEC Companyfacts API para una cohorte de compañías comparables. La muestra procesada tendrá compañía, período, ventas, costo de ventas, cuentas por cobrar, inventario, cuentas por pagar, flujo operativo y capex.

Evidencia:

- extracción con user agent y tags XBRL alternativos;
- deduplicación por período y filing;
- DSO, DIO, DPO y CCC con saldos promedio;
- comparación interanual;
- scatter de crecimiento de ventas vs. variación del CCC;
- conciliaciones de fórmulas y cobertura.

La figura tendrá al menos 12 observaciones comparables. Los resultados no presentarán el dato SEC como homogeneizado o auditado por el portfolio.

## Proyecto 2 — Reclamos financieros en SQL

Fuente: CFPB Consumer Complaint Database API. La muestra contendrá miles de reclamos y conservará complaint ID, fechas, producto, issue, empresa, canal y respuesta oportuna.

Evidencia:

- ingesta a DuckDB;
- staging, tipado, deduplicación y métricas implementados en SQL;
- `ROW_NUMBER`, `LAG`, ventana móvil, percentiles y ranking;
- pruebas de unicidad, fechas y denominadores;
- heatmap producto-problema y cola operativa;
- script opcional para cargar el archivo histórico completo.

Python solo orquesta DuckDB y dibuja el resultado ya agregado.

## Proyecto 3 — Finanzas conductuales

Fuente: CFPB National Financial Well-Being Survey PUF. La muestra usará variables reales de bienestar, habilidad, conocimiento, ahorro, horizonte, resiliencia, ingreso y peso.

Evidencia:

- tratamiento explícito de códigos faltantes;
- segmentación reproducible sobre dimensiones interpretables;
- estabilidad por semillas;
- regresión descriptiva con controles;
- perfiles y diferencia de bienestar por segmento;
- gráfico de conocimiento objetivo vs. confianza.

Todo lenguaje será asociativo. La segmentación no se propondrá para decisiones adversas.

## Proyecto 4 — Riesgo de pago B2B

Fuente: generador sintético documentado, calibrado con estadísticas públicas de prácticas de pago. La demo tendrá al menos 20.000 facturas y 36 meses.

Evidencia:

- generación determinística y conciliaciones;
- snapshots que excluyen información futura;
- split temporal train/validation/test;
- regresión logística y baselines;
- PR-AUC, Brier score, calibración, lift e importe capturado;
- política por capacidad y valor esperado;
- gain curve y model card.

Las pruebas bloquearán features posteriores a la emisión.

## Proyecto 5 — Anomalías de gasto

Fuente: Parquet derivado de Checkbook NYC y publicado por DataBook NYC, con trazabilidad a la API oficial. Se usará una muestra real de transacciones.

Evidencia:

- reglas de duplicado, repetición temporal, redondeo y concentración;
- features por peer group;
- Isolation Forest como señal secundaria;
- inyección separada de anomalías para evaluar detección sin inventar fraude real;
- precision/recall en top K sobre la validación inyectada;
- matriz exposición vs. fuerza de evidencia;
- reason codes y cola de revisión.

Los outputs separarán “señalado” de “confirmado”.

## Visualización

Las cinco figuras usarán un sistema común:

- fondo claro, tinta oscura y una raíz azul;
- segunda raíz naranja solo para foco o alerta;
- títulos descriptivos, subtítulos con unidad/alcance y fuente;
- ejes honestos, denominadores visibles y sin efectos 3D;
- PNG de al menos 1400 × 800 px.

Cada figura se inspeccionará en su formato final.

## Notebooks

Cada notebook seguirá:

1. `tl;dr`;
2. `Context & Methods`;
3. `Data`;
4. `Results`;
5. `Takeaways`.

Los notebooks importarán el paquete instalado, ejecutarán el análisis offline y mostrarán métricas y figura. Se ejecutarán con `nbclient`; no se publicarán notebooks con errores o conclusiones no respaldadas por outputs.

## Pruebas y validación

La suite cubrirá:

- fórmulas de capital de trabajo;
- unicidad y métricas SQL;
- determinismo y estabilidad de segmentación;
- ausencia de leakage y split temporal;
- reason codes y detección de anomalías inyectadas;
- presencia de artefactos y notebooks ejecutados;
- cinco briefs, ocho secciones, fuentes y navegación.

La entrega se considera lista cuando:

- `make all` termina con código 0;
- todas las pruebas pasan;
- cada notebook tiene outputs ejecutados;
- cada `metrics.json` contiene resultados finitos;
- las cinco figuras fueron inspeccionadas;
- el README raíz muestra resultados reales y enlaza la evidencia.

## Honestidad y alcance

La demo prueba capacidad técnica y reproducibilidad; no sustituye una implementación productiva. Los samples reducen escala, los modelos no se despliegan y no se afirma causalidad ni fraude. Los scripts de refresh permiten ampliar el análisis sobre la fuente completa.

# Portfolio de análisis de datos con criterio de negocio

[![CI](https://github.com/selimb1/portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/selimb1/portfolio/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-1f5aa6.svg)](pyproject.toml)
[![Reproducible](https://img.shields.io/badge/análisis-reproducibles-16836b.svg)](Makefile)

Cinco proyectos para demostrar **SQL, Python/Pandas, visualización, estadística y storytelling con datos** desde una perspectiva poco genérica: contabilidad, finanzas, riesgo y economía conductual.

El hilo conductor no es “qué técnica sé usar”, sino **qué decisión puedo mejorar**. Cada caso parte de una pregunta ejecutiva, explicita las limitaciones de los datos y termina en una acción medible.

> **Para recruiters:** cada resultado de portada está calculado, no redactado como placeholder. Se puede abrir el notebook ejecutado, inspeccionar el dato, revisar el código y correr la prueba asociada.

## Resumen de los 5 proyectos

| Nivel | Proyecto | Resultado ejecutado | Datos | Stack observable | Qué demuestra |
|---:|---|---|---|---|---|
| 1 | [Rentabilidad no es caja](projects/01-working-capital/README.md) | USD 26,8 M de caja asociados a 0,22 días de deterioro del CCC | 16 estados anuales públicos | Pandas + ratios contables + tests | Criterio contable y narrativa CFO |
| 2 | [El costo oculto del reclamo](projects/02-complaint-risk-sql/README.md) | Cola explicable sobre 20.000 reclamos | CFPB, 479 empresas | DuckDB + SQL puro + ventanas | SQL analítico y prudencia regulatoria |
| 3 | [La brecha entre saber y hacer](projects/03-behavioral-finance/README.md) | 29,6 puntos entre segmentos; ARI 0,945 | CFPB, 6.394 personas | Pandas + K-Means + regresión ponderada | Economía conductual e inferencia responsable |
| 4 | [Cobrar antes de perseguir](projects/04-payment-risk/README.md) | Lift 2,26× en el decil superior | 20.000 facturas sintéticas auditables | Pipeline + regresión logística + backtest | Predicción explicable y decisión de cobranza |
| 5 | [Cada peso deja una huella](projects/05-spend-anomalies/README.md) | 250 casos concentran USD 6.742 M; recall inyectado 92% | 25.000 pagos públicos NYC | Reglas + Isolation Forest + reason codes | Auditoría, explicabilidad y seniority |

## Evidencia técnica observable

| Proyecto | Datos y trazabilidad | Notebook ejecutado | Código principal | Tests | Resultado verificable |
|---|---|---|---|---|---|
| Capital de trabajo | [muestra](projects/01-working-capital/data/sample.csv) · [fuente](projects/01-working-capital/data/source.json) | [abrir](projects/01-working-capital/notebooks/analysis.ipynb) | [Python](src/portfolio_analytics/working_capital.py) | [unitarios](tests/test_working_capital.py) | [métricas](projects/01-working-capital/outputs/metrics.json) |
| Reclamos SQL | [muestra](projects/02-complaint-risk-sql/data/sample.csv) · [fuente](projects/02-complaint-risk-sql/data/source.json) | [abrir](projects/02-complaint-risk-sql/notebooks/analysis.ipynb) | [SQL](projects/02-complaint-risk-sql/sql/risk_queue.sql) · [runner](src/portfolio_analytics/complaint_sql.py) | [unitarios](tests/test_complaint_sql.py) | [cola](projects/02-complaint-risk-sql/outputs/risk_queue.csv) |
| Finanzas conductuales | [muestra](projects/03-behavioral-finance/data/sample.csv) · [fuente](projects/03-behavioral-finance/data/source.json) | [abrir](projects/03-behavioral-finance/notebooks/analysis.ipynb) | [Python](src/portfolio_analytics/behavioral_finance.py) | [unitarios](tests/test_behavioral_finance.py) | [perfiles](projects/03-behavioral-finance/outputs/segment_profiles.csv) |
| Riesgo de pago | [muestra](projects/04-payment-risk/data/sample.csv) · [generador](projects/04-payment-risk/data/source.json) | [abrir](projects/04-payment-risk/notebooks/analysis.ipynb) | [Python](src/portfolio_analytics/payment_risk.py) | [unitarios](tests/test_payment_risk.py) | [predicciones](projects/04-payment-risk/outputs/payment_risk_predictions.csv) · [model card](projects/04-payment-risk/outputs/model_card.md) |
| Anomalías de gasto | [muestra](projects/05-spend-anomalies/data/sample.csv) · [fuente](projects/05-spend-anomalies/data/source.json) | [abrir](projects/05-spend-anomalies/notebooks/analysis.ipynb) | [Python](src/portfolio_analytics/spend_anomalies.py) | [unitarios](tests/test_spend_anomalies.py) | [cola](projects/05-spend-anomalies/outputs/review_queue.csv) |

### Reproducir todo

```bash
make setup
make all
```

`make all` vuelve a calcular los cinco casos con las muestras versionadas, ejecuta los notebooks, corre la suite de pruebas y valida la estructura completa. [GitHub Actions](.github/workflows/ci.yml) repite el mismo control en cada cambio.

## La historia que cuenta el portfolio

### 1. Rentabilidad no es caja

Un radar de capital de trabajo que traduce estados contables en señales tempranas de liquidez. Responde si el crecimiento se financia con caja propia, proveedores o mayor plazo de cobro.

**Decisión que habilita:** dónde concentrar una revisión de cobranzas, inventarios o negociación con proveedores.

[Ver el brief completo →](projects/01-working-capital/README.md)

### 2. El costo oculto del reclamo

Un caso SQL-first sobre 20.000 reclamos financieros reales: desde el archivo normalizado hasta ventanas, tasas de respuesta tardía y un backlog priorizado por riesgo operativo.

**Decisión que habilita:** qué producto, problema, canal y geografía debe entrar primero en un plan de remediación.

[Ver el brief completo →](projects/02-complaint-risk-sql/README.md)

### 3. La brecha entre saber y hacer

Una segmentación que separa capacidad económica de conducta: dos personas con ingresos parecidos pueden necesitar intervenciones totalmente distintas por sus hábitos, confianza y resiliencia.

**Decisión que habilita:** qué mensaje, producto o intervención usar para cada perfil conductual.

[Ver el brief completo →](projects/03-behavioral-finance/README.md)

### 4. Cobrar antes de perseguir

Un modelo simple de mora B2B que solo usa información disponible al emitir la factura. La salida no es un score abstracto, sino una política de cobranza con costos, capacidad y valor esperado.

**Decisión que habilita:** a qué factura contactar, cuándo y con qué intensidad.

[Ver el brief completo →](projects/04-payment-risk/README.md)

### 5. Cada peso deja una huella

Un sistema de monitoreo que combina reglas contables y anomalías estadísticas para transformar miles de pagos en una cola explicable de revisión.

**Decisión que habilita:** qué transacciones investigar primero y por qué señal.

[Ver el brief completo →](projects/05-spend-anomalies/README.md)

## Cobertura de competencias

| Requisito | Proyecto(s) que lo demuestran |
|---|---|
| SQL y modelado de datos | 1, **2**, 4 y 5 |
| Python/Pandas | 1, 3, 4 y 5 |
| Visualización y dashboards | Los cinco |
| Estadística aplicada | 1, 3, 4 y 5 |
| Storytelling con datos | Los cinco, con una decisión ejecutiva explícita |
| Contabilidad, finanzas o fiscalidad | **1, 2, 4 y 5** |
| Economía/finanzas conductual | **3** |
| SQL puro sobre datos voluminosos | **2** |
| Modelo predictivo simple | **4**, con regresión logística explicada por costo de decisión |
| Señal de seniority | **5**, por integrar ingesta, controles, modelo y workflow de auditoría |

## Cómo leer y construir estos proyectos

Cada brief contiene exactamente:

1. título y pitch;
2. fuente y estrategia de datos;
3. preguntas de negocio;
4. stack técnico;
5. análisis paso a paso;
6. dashboard o gráfico final;
7. frase de insight para el portfolio;
8. dificultad y señal profesional.

Además, define unidad de análisis, KPI, controles metodológicos, entregables y criterio de finalización. La recomendación es construirlos en orden: cada uno suma una capacidad nueva sin repetir el anterior.

## Honestidad analítica

Este repositorio contiene **resultados calculados y reproducibles**. Cuatro casos usan muestras reales y públicas; el caso de mora usa datos sintéticos porque no existe un historial B2B abierto con el detalle necesario. Esa simulación tiene semilla, reglas, contrato y límites explícitos.

Los rankings de reclamos y anomalías son colas de investigación, no acusaciones. La segmentación conductual describe asociaciones, no causalidad. El modelo de mora es un backtest sintético, no una promesa de impacto en producción. Esas distinciones son parte de la evidencia de juicio profesional.

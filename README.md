# Portfolio de análisis de datos con criterio de negocio

Cinco proyectos para demostrar **SQL, Python/Pandas, visualización, estadística y storytelling con datos** desde una perspectiva poco genérica: contabilidad, finanzas, riesgo y economía conductual.

El hilo conductor no es “qué técnica sé usar”, sino **qué decisión puedo mejorar**. Cada caso parte de una pregunta ejecutiva, explicita las limitaciones de los datos y termina en una acción medible.

## Resumen de los 5 proyectos

| Nivel | Proyecto | Problema de negocio | Datos | Stack recomendado | Qué demuestra |
|---:|---|---|---|---|---|
| 1 | [Rentabilidad no es caja](projects/01-working-capital/README.md) | Detectar cuándo el crecimiento está consumiendo liquidez antes de que aparezca una crisis de caja | Estados financieros SEC/XBRL | SQL + Python/Pandas + Power BI | Criterio contable, KPIs de capital de trabajo y narrativa CFO |
| 2 | [El costo oculto del reclamo](projects/02-complaint-risk-sql/README.md) | Priorizar fallas operativas y regulatorias en productos financieros | CFPB Consumer Complaint Database | PostgreSQL o BigQuery + SQL puro + Metabase | Modelado dimensional, ventanas, cohortes y análisis a escala |
| 3 | [La brecha entre saber y hacer](projects/03-behavioral-finance/README.md) | Segmentar clientes por conducta financiera para diseñar intervenciones más efectivas | CFPB Financial Well-Being Survey | Python/Pandas + scikit-learn + statsmodels + Tableau | Economía conductual, estadística y segmentación interpretable |
| 4 | [Cobrar antes de perseguir](projects/04-payment-risk/README.md) | Predecir qué facturas se pagarán tarde y asignar el esfuerzo de cobranza por valor esperado | Facturas B2B sintéticas, generadas con reglas auditables | SQL + Python + scikit-learn + Power BI | Clasificación explicable, validación temporal y política de decisión |
| 5 | [Cada peso deja una huella](projects/05-spend-anomalies/README.md) | Detectar pagos y proveedores que merecen revisión sin confundir anomalía con fraude | Checkbook NYC API | Python + DuckDB + SQL + Isolation Forest + Tableau | Data pipeline, controles contables, anomalías y priorización de auditoría |

## La historia que cuenta el portfolio

### 1. Rentabilidad no es caja

Un radar de capital de trabajo que traduce estados contables en señales tempranas de liquidez. Responde si el crecimiento se financia con caja propia, proveedores o mayor plazo de cobro.

**Decisión que habilita:** dónde concentrar una revisión de cobranzas, inventarios o negociación con proveedores.

[Ver el brief completo →](projects/01-working-capital/README.md)

### 2. El costo oculto del reclamo

Un caso SQL-first sobre millones de reclamos financieros: desde el archivo crudo hasta cohortes, tasas de respuesta tardía y un backlog priorizado por riesgo operativo.

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

## Nota de honestidad analítica

Este repositorio contiene **diseños de proyectos reproducibles**, no resultados ya calculados. Las frases de insight usan campos como `[X días]` o `[Y%]` para evitar inventar hallazgos. Esos campos se reemplazan únicamente después de ejecutar el análisis y validar el resultado.

Los datos voluminosos no se versionan aquí. Cada proyecto enlaza la fuente pública oficial o, cuando el dato no existe de forma abierta, documenta una simulación reproducible con reglas contables y semilla fija.

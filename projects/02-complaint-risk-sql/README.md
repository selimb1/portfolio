[← Volver al portfolio](../../README.md)

# El costo oculto del reclamo

## 1. Título y pitch

**El costo oculto del reclamo — Riesgo operativo financiero en SQL**

Convierte millones de reclamos de consumidores en un mapa de fallas operativas para decidir dónde intervenir antes de que escalen el costo, la fricción y el riesgo regulatorio.

**Decisión que habilita:** priorizar el backlog de remediación por producto, problema, canal, geografía y tendencia.

## 2. Fuente de datos

**Fuente real, pública y actualizable:** [CFPB Consumer Complaint Database](https://www.consumerfinance.gov/data-research/consumer-complaints/), disponible para descarga y consulta mediante API.

La base contiene reclamos enviados por consumidores sobre productos y servicios financieros, junto con producto, problema, empresa, geografía, canal, respuesta de la empresa y una señal de respuesta oportuna.

Alcance recomendado:

- archivo histórico completo para demostrar escala;
- actualización mensual incremental;
- unidad de análisis: `complaint_id`;
- período analítico principal: últimos 36 meses, conservando el histórico para tendencias;
- PostgreSQL para practicar operación real o BigQuery si se prioriza procesamiento administrado.

## 3. Preguntas de negocio

- ¿Qué combinaciones de producto y problema explican el crecimiento reciente de reclamos?
- ¿Dónde aumenta la proporción de respuestas no oportunas?
- ¿Qué canales generan más fricción de enrutamiento entre recepción y envío a la empresa?
- ¿Qué problemas cambian de forma persistente y cuáles son ruido mensual?
- ¿Qué estados o regiones concentran una mezcla inusual de problemas?
- ¿Qué cohortes de reclamos requieren revisión primero si la capacidad operativa es limitada?
- ¿La aparente diferencia entre empresas se explica por mezcla de productos y volumen observado?

**KPI principal:** tasa de respuesta no oportuna, acompañada por volumen, cambio interanual, mix de problemas y antigüedad de la cohorte.

## 4. Stack técnico

- **PostgreSQL 16 o BigQuery:** todo el pipeline analítico.
- **SQL puro:** carga, tipado, calidad, modelo dimensional, ventanas, cohortes, percentiles y tablas de serving.
- **Metabase, Superset o Looker Studio:** visualización conectada a vistas SQL.
- **Git:** scripts numerados y ejecutables en orden.

El desafío impone una regla: **Python no transforma datos**. Puede usarse una herramienta de línea de comandos para descargar el CSV, pero desde el staging hasta el dashboard la lógica vive en SQL revisable.

## 5. Estructura del análisis

### Paso 1 — Carga reproducible

Crear una tabla `stg_complaints_raw` inicialmente textual para que valores inesperados no rompan la ingesta. Registrar fecha de descarga, nombre de archivo, filas cargadas y hash.

Después, insertar a una tabla tipada:

```text
fact_complaint
├── complaint_id
├── date_received
├── date_sent_to_company
├── product / sub_product
├── issue / sub_issue
├── company
├── state / zip_code
├── submitted_via
├── company_response
├── timely_response
└── consumer_narrative_available
```

### Paso 2 — Auditoría de calidad en SQL

- unicidad y nulidad de `complaint_id`;
- fechas imposibles o envío anterior a recepción;
- cambios de categorías a lo largo del tiempo;
- porcentaje de nulos por campo y mes;
- volumen de duplicados;
- cobertura temporal;
- conciliación entre filas del archivo y filas cargadas.

Crear una tabla `data_quality_run` para conservar el resultado de cada actualización.

### Paso 3 — Modelo analítico

Separar dimensiones conformadas de producto, problema, empresa, geografía, canal y fecha. Conservar etiquetas originales y crear una taxonomía estable para categorías que hayan cambiado.

Materializar:

- `fct_complaints`;
- `agg_complaints_monthly`;
- `agg_issue_cohort`;
- `mart_operational_risk_queue`.

### Paso 4 — SQL que debe lucirse

El repositorio debe incluir ejemplos de:

- `ROW_NUMBER()` para deduplicación determinística;
- `LAG()` y ventanas móviles de 3/12 meses;
- cohortes por mes de recepción;
- `GROUPING SETS` para totales compatibles;
- `PERCENT_RANK()` para señalar cambios extremos;
- medias suavizadas con denominadores explícitos;
- índices o particiones guiados por `EXPLAIN`;
- pruebas SQL de unicidad, relaciones y valores aceptados.

### Paso 5 — Métricas sin trampas

Calcular:

- volumen mensual e interanual;
- tasa de respuesta no oportuna;
- días entre recepción y envío a la empresa, descritos como **demora de enrutamiento**, no como tiempo de resolución;
- participación de producto/problema dentro de los reclamos observados;
- cambio de mix;
- señal de aceleración: promedio de 3 meses vs. promedio de 12 meses.

No usar conteos brutos para afirmar que una empresa “es peor”: la base no contiene cantidad de clientes, transacciones o cuota de mercado.

### Paso 6 — Priorización

Construir una cola explicable con cuatro componentes normalizados:

1. volumen reciente;
2. aceleración;
3. tasa no oportuna;
4. persistencia durante al menos tres meses.

El puntaje sirve para ordenar investigación operativa, no para emitir una conclusión regulatoria.

### Paso 7 — Storytelling

Empezar por “dónde crece”, seguir con “qué problema lo explica” y cerrar con “qué cola de trabajo debería cambiar mañana”. Mostrar tanto tasa como denominador en cada vista.

### Controles metodológicos

- Los reclamos no son una muestra representativa de todos los clientes.
- Las narrativas expresan alegaciones del consumidor y no hechos verificados.
- Comparar tasas solo con un mínimo de observaciones visible.
- No atribuir causalidad a cambios regulatorios o de producto sin un diseño adicional.
- Mantener una tabla de cambios de taxonomía.
- Evitar información personal y no publicar narrativas crudas en el dashboard.

## 6. Visualización final

Un **centro de control de riesgo operativo**:

- tarjetas: reclamos del mes, variación interanual, tasa no oportuna y problemas en aceleración;
- heatmap `producto × problema`, coloreado por aceleración y filtrable por volumen;
- línea de 36 meses con promedio móvil y bandas históricas;
- matriz de cohortes por mes de recepción;
- tabla priorizada con producto, problema, volumen, tasa, persistencia y razón del puntaje;
- vista geográfica normalizada dentro del universo de reclamos.

El gráfico principal debe ser el heatmap: permite pasar de “subieron los reclamos” a “esta combinación concreta explica el cambio”.

## 7. Frase para el portfolio

> “El aumento total ocultaba una concentración operativa: **[producto + problema]** explicó **[X%]** del crecimiento reciente y sostuvo una tasa de respuesta no oportuna de **[Y%]** durante **[N meses]**; por eso pasó al primer lugar de la cola de remediación.”

Los campos se reemplazan con resultados del pipeline. La frase no debe convertirse en un ranking de calidad empresarial sin datos de exposición.

## 8. Nivel de dificultad

**Nivel 2 de 5 — SQL a escala con criterio de riesgo.**

Demuestra que SQL no es solo seleccionar filas: incluye diseño de tablas, calidad, ventanas, cohortes, optimización y una capa de decisión consumible.

### Entregables

- scripts `00_schema` a `06_serving`;
- diagrama de modelo;
- consultas de calidad y resultados de `EXPLAIN`;
- diccionario de métricas;
- dashboard;
- memo con tres acciones y tres limitaciones.

### Criterio de finalización

El proyecto está listo cuando una carga completa y una incremental producen los mismos agregados, cada tarjeta concilia con una consulta de control y la cola explica por qué cada segmento fue priorizado.

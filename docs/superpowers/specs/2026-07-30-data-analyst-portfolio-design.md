# Diseño del portfolio de análisis de datos con criterio financiero

## Objetivo

Transformar un repositorio vacío en una propuesta de cinco proyectos de portfolio que demuestre habilidades técnicas de análisis de datos y, al mismo tiempo, un diferencial contable-financiero y de economía conductual. El resultado debe permitir que un reclutador entienda rápidamente qué problema resuelve cada proyecto, cómo se ejecutaría y qué decisión de negocio habilita.

## Audiencia y tono

La audiencia principal son responsables de Analytics, Finanzas, Riesgo, Operaciones y recruiters de perfiles de datos. El contenido se escribirá en español, con títulos memorables, lenguaje ejecutivo y suficiente detalle técnico para demostrar profundidad sin convertir la portada en documentación de implementación.

## Estructura editorial

El repositorio tendrá dos capas:

1. `README.md`: propuesta de valor, tabla comparativa de los cinco proyectos, cobertura de habilidades y enlaces a cada brief.
2. `projects/<proyecto>/README.md`: desarrollo completo de los ocho puntos solicitados, más criterios de reproducibilidad, riesgos metodológicos y entregables.

Esta estructura permite una lectura de menos de dos minutos en portada y una evaluación técnica profunda por proyecto.

## Selección de proyectos

| Nivel | Proyecto | Fuente principal | Competencia dominante |
|---:|---|---|---|
| 1 | Rentabilidad no es caja | SEC Financial Statement Data Sets / Companyfacts | Contabilidad, Pandas y storytelling |
| 2 | El costo oculto del reclamo | CFPB Consumer Complaint Database | SQL puro sobre datos voluminosos |
| 3 | La brecha entre saber y hacer | CFPB National Financial Well-Being Survey | Economía conductual y segmentación |
| 4 | Cobrar antes de perseguir | Generador reproducible de facturas B2B | Clasificación explicable y decisiones de cobranza |
| 5 | Cada peso deja una huella | Checkbook NYC API | Controles, anomalías y priorización de auditoría |

La secuencia aumenta en ambición: comienza con diagnóstico descriptivo acotado, suma escala y diseño analítico, incorpora comportamiento y causalidad prudente, introduce predicción accionable y termina con un sistema de monitoreo de riesgo.

## Criterios de contenido por brief

Cada brief incluirá, en este orden:

1. Título y pitch.
2. Fuente de datos, acceso, granularidad y alternativa reproducible.
3. Preguntas de negocio.
4. Stack técnico.
5. Análisis paso a paso: adquisición, validación, limpieza, EDA, modelado cuando corresponda, visualización y conclusiones.
6. Diseño del dashboard o gráfico final.
7. Frase de insight para portfolio.
8. Nivel de dificultad y señal de seniority.

También incluirá:

- decisión concreta que habilita;
- unidad de análisis y KPI principal;
- controles contra fuga de información, sesgo o comparaciones inválidas;
- entregables mínimos;
- criterio objetivo de finalización.

## Honestidad analítica

Los proyectos son diseños, no análisis ya ejecutados. Por eso, ninguna frase afirmará resultados numéricos inexistentes. Las frases de insight usarán variables visibles —por ejemplo, `[X días]` o `[Y%]`— y explicarán qué relación debe completarse después de ejecutar el notebook o las consultas.

Las fuentes públicas se enlazarán a páginas oficiales. Se aclarará que:

- los datos SEC se publican “as filed” y requieren normalizar conceptos XBRL;
- los reclamos CFPB no representan prevalencia de mercado sin denominadores de exposición;
- una encuesta observacional permite asociaciones, no causalidad;
- los datos B2B sintéticos validan el pipeline, no prueban desempeño en una empresa real;
- una anomalía estadística es una señal de revisión, no evidencia de fraude.

## Reproducibilidad

Cada proyecto especificará:

- período y alcance recomendados;
- claves de unión y unidad de observación;
- diccionario mínimo de variables;
- pasos de ingesta y transformación;
- semilla fija cuando haya simulación o modelado;
- división temporal para el modelo de mora;
- validaciones de calidad;
- artefactos esperados: consultas, notebook, tabla analítica, dashboard y README.

No se incluirán datasets pesados ni datos personales en el repositorio. Los briefs indicarán cómo descargarlos desde la fuente oficial o generarlos.

## Navegación y presentación

La portada usará una tabla compacta con nivel, proyecto, problema, datos, stack y señal principal. Debajo mostrará una matriz de cobertura para probar explícitamente que los requisitos se cumplen. Los briefs tendrán enlaces de retorno a la portada y una jerarquía consistente de encabezados.

## Verificación

Antes de publicar se comprobará:

- que existen cinco proyectos y todos contienen los ocho apartados;
- que hay al menos dos proyectos financiero-contables;
- que uno cubre economía conductual;
- que uno prioriza SQL puro sobre un dataset voluminoso;
- que uno usa clasificación explicable en términos económicos;
- que todas las fuentes oficiales y enlaces internos responden o apuntan a rutas existentes;
- que no se presentan números simulados como hallazgos reales;
- que el Markdown se renderiza sin enlaces rotos ni tablas incompletas.

## Fuera de alcance

Esta entrega diseña el portfolio y sus hojas de ruta reproducibles. No descarga datasets completos, no ejecuta los cinco análisis, no produce modelos entrenados ni publica dashboards externos. Esos entregables conforman la siguiente etapa natural de implementación proyecto por proyecto.

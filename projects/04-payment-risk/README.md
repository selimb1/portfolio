[← Volver al portfolio](../../README.md)

# Cobrar antes de perseguir

## 1. Título y pitch

**Cobrar antes de perseguir — Predicción explicable de mora B2B**

Predice, al emitir una factura, cuáles tienen mayor probabilidad de pagarse con más de 15 días de atraso y convierte ese riesgo en una política de cobranza rentable.

**Decisión que habilita:** asignar contactos preventivos y capacidad del equipo según riesgo, importe y costo esperado.

## 2. Fuente de datos

No suele existir un dataset público de cuentas por cobrar B2B con historial, condiciones comerciales y pagos por factura. Por eso se propone un **generador sintético reproducible**, diseñado con reglas contables explícitas.

Escala recomendada:

- 2.000 clientes;
- 250.000 facturas;
- 36 meses;
- semilla fija;
- unidad de análisis: factura al momento de emisión.

Tablas:

```text
customers
customer_id, industry, region, size_band, onboarding_date,
credit_limit, agreed_terms, latent_risk_band

invoices
invoice_id, customer_id, issue_date, due_date, amount,
currency, payment_terms, product_family, payment_date,
dispute_flag, write_off_flag

events
invoice_id, event_at, event_type, channel

macro_monthly
month, policy_rate, inflation_proxy, activity_index
```

Reglas realistas:

- importes con distribución lognormal y límites por tamaño de cliente;
- términos de 15, 30, 45, 60 y 90 días;
- propensión de atraso persistente por cliente;
- mayor riesgo ante exposición abierta alta, disputas previas y shocks macro;
- estacionalidad de fin de año;
- clientes nuevos con poco historial;
- pagos parciales y faltantes controlados;
- cambio de política de cobranza a mitad del período.

El generador debe publicar las reglas y una tabla de balance contable para que la simulación sea auditable.

## 3. Preguntas de negocio

- ¿Qué facturas corren riesgo de superar 15 días de atraso al momento de emisión?
- ¿Qué variables explican el riesgo sin usar información del futuro?
- ¿Cuánto mejora una política predictiva respecto de contactar por mayor importe o antigüedad?
- ¿Dónde ubicar el umbral si un contacto tiene costo y también puede generar fricción?
- ¿Qué porcentaje del importe en riesgo captura el equipo con capacidad limitada?
- ¿El modelo sigue calibrado en clientes nuevos, industrias y meses de estrés?
- ¿Cuánto efectivo podría adelantarse bajo escenarios conservadores de eficacia?

**KPI principal:** importe vencido esperado capturado dentro de la capacidad del equipo, no accuracy.

## 4. Stack técnico

- **SQL (PostgreSQL o DuckDB):** snapshots de cuentas por cobrar y features históricas.
- **Python + Pandas:** generador, validación, EDA y backtesting.
- **scikit-learn:** regresión logística, calibración y benchmark.
- **statsmodels:** lectura económica de coeficientes.
- **MLflow opcional:** registro de experimento y fecha de corte.
- **Power BI:** cartera, bandas de riesgo y cola de acciones.

El modelo principal es deliberadamente simple: una regresión logística bien calibrada y explicable aporta más valor que un algoritmo complejo sin política de decisión.

## 5. Estructura del análisis

### Paso 1 — Definir el momento de decisión

La predicción ocurre al emitir la factura. Solo se permiten datos existentes hasta `issue_date`.

**Prohibidos por fuga de información:**

- fecha de pago;
- recordatorios posteriores a la emisión;
- disputa iniciada después de la emisión;
- estado de cobranza futuro;
- saldo abierto calculado con eventos posteriores.

Crear snapshots “as of” para demostrar que cada feature respeta el corte.

### Paso 2 — Generar y validar los datos

- fijar semilla y versión del generador;
- conciliar facturas, pagos, notas de crédito y write-offs;
- comprobar que `payment_date ≥ issue_date`;
- validar límites de crédito y monedas;
- comparar distribuciones con parámetros esperados;
- generar un “data card” que separe variables simuladas de derivadas.

El objetivo `late_15` vale 1 si el pago final ocurre más de 15 días después del vencimiento o permanece impago al cierre de observación.

### Paso 3 — EDA de cartera

- aging 0, 1–15, 16–30, 31–60, 61–90 y 90+;
- tasa e importe de mora por cohorte de emisión;
- atraso por términos, industria y antigüedad del cliente;
- concentración de exposición;
- transición entre bandas de atraso;
- impacto del shock macro y del cambio de política simulado.

### Paso 4 — Features disponibles

Calcular en SQL, siempre con historia anterior:

- cantidad de facturas previas;
- tasa histórica de atraso;
- mediana y percentil 90 de días de atraso;
- importe abierto y utilización del límite;
- disputas previas;
- días desde alta;
- monto relativo a la factura típica del cliente;
- términos, industria, región y mes;
- variables macro conocidas en la fecha.

Para clientes nuevos, usar señales contractuales y promedios jerárquicos calculados solo en entrenamiento.

### Paso 5 — Corte temporal y baseline

- entrenamiento: meses 1–24;
- validación: meses 25–30;
- test final: meses 31–36;
- dejar un período de maduración para no etiquetar como puntual una factura aún no observable.

Comparar contra:

1. contactar las facturas de mayor importe;
2. regla fija por utilización de crédito;
3. tasa histórica del cliente;
4. regresión logística.

### Paso 6 — Modelo y evaluación

- imputación dentro del pipeline;
- one-hot para categorías;
- estandarización de continuas;
- regularización;
- calibración con validación temporal;
- coeficientes y odds ratios con dirección económica.

Métricas:

- PR-AUC y ROC-AUC como diagnóstico;
- Brier score y curva de calibración;
- lift y recall en el top 5%, 10% y 20%;
- importe capturado;
- costo y valor esperado de la política.

### Paso 7 — Umbral económico

Definir:

```text
beneficio esperado =
P(mora) × importe × eficacia_contacto × costo_financiero_del_atraso
− costo_contacto
− costo_esperado_de_fricción
```

Seleccionar el umbral sujeto a capacidad diaria. Ejecutar sensibilidad con distintas eficacias; la simulación no demuestra que el contacto cause el pago.

Bandas sugeridas:

- **baja:** seguimiento automático;
- **media:** recordatorio preventivo;
- **alta:** revisión humana antes del vencimiento;
- **alta + importe material:** plan de cuenta con Finanzas y Ventas.

### Paso 8 — Monitoreo

Control mensual de calibración, mora base, mix, nulos, performance por segmento y deriva de features. Definir gatillos de reentrenamiento y un fallback a reglas si el pipeline falla.

### Controles metodológicos

- Evitar toda variable posterior al momento de decisión.
- Medir por tiempo, nunca con split aleatorio.
- Mostrar importe y cantidad; una buena tasa puede ocultar grandes facturas.
- Revisar desempeño en clientes nuevos y segmentos pequeños.
- No presentar datos sintéticos como evidencia de impacto real.
- Validar la eficacia de la acción con un experimento controlado antes de atribuir cobros al modelo.

## 6. Visualización final

Un **cockpit de cobranzas por valor esperado**:

- tarjetas: exposición total, importe en riesgo, capacidad usada y valor esperado;
- gráfico principal: curva de ganancia `porcentaje de facturas contactadas vs. porcentaje de importe moroso capturado`;
- matriz `probabilidad × importe` con banda de acción;
- curva de calibración;
- aging por cohorte;
- tabla operativa con factura, riesgo, importe, factores y acción sugerida;
- monitoreo de performance y drift por mes.

La curva de ganancia debe comparar modelo, regla por importe y selección aleatoria. Así el lector ve la utilidad operativa, no solo una métrica técnica.

## 7. Frase para el portfolio

> “Con capacidad para contactar solo **[X%]** de las facturas, la política capturó **[Y%]** del importe que terminaría 15+ días vencido, **[Z puntos]** más que priorizar únicamente por monto, manteniendo calibrado el riesgo por segmento.”

La frase describe un backtest sobre datos sintéticos. Debe rotularse como tal hasta validarla en datos reales.

## 8. Nivel de dificultad

**Nivel 4 de 5 — Modelo predictivo convertido en política.**

La señal de madurez no está en el algoritmo: está en definir el corte temporal, evitar leakage, calibrar probabilidades, valorar errores y conectar el score con una capacidad operativa.

### Entregables

- generador sintético y data card;
- pruebas de conciliación y fuga de información;
- SQL de snapshots y features;
- notebook de EDA, entrenamiento y backtest;
- modelo serializado y ficha de modelo;
- dashboard y playbook de acciones.

### Criterio de finalización

El proyecto está listo cuando el modelo supera los baselines en un test temporal, las probabilidades están calibradas, ninguna feature mira al futuro y la política mejora el valor esperado bajo al menos tres escenarios de costo y capacidad.

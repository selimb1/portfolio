# Model card — Riesgo de pago tardío

## Uso previsto

Priorizar recordatorios y revisión humana; no rechazar crédito.

## Diseño

Regresión logística entrenada en el 80% temporal inicial y evaluada en el 20% más reciente. Solo usa información disponible al emitir la factura.

## Límites

Datos sintéticos, drift no monitoreado y probabilidades no válidas para otra cartera sin recalibración. Deben auditarse desempeño y trato por segmento.

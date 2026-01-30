# Contrato de entrada/salida del generador (v1)

Este contrato formaliza el esquema de datos permitido para invocar el generador y el formato esperado de salida. Su finalidad es evitar que el modelo invente datos fuera de la guía.

## 1) Esquema de entrada (JSON)

**Campos permitidos** (solo estos pueden ser provistos al generador):

```json
{
  "patient_name": "Juan",
  "mdls_calculable": true,
  "mdls_tier": "MEDIO",
  "biomarker_risk_tier": null,
  "days_since_last_exam": 120,
  "recency_type": "HISTORICO"
}
```

### 1.1 Reglas de validación
- `patient_name`: string no vacío.
- `mdls_calculable`: boolean.
- `mdls_tier`: enum `BAJO | MEDIO | ALTO` (obligatorio si `mdls_calculable = true`).
- `biomarker_risk_tier`: enum `BAJO | MEDIO | ALTO` (obligatorio si `mdls_calculable = false`).
- `days_since_last_exam`: integer >= 0.
- `recency_type`: enum `PRIMER_EXAMEN | HISTORICO`.

### 1.2 Restricciones del esquema
- No se aceptan biomarcadores ni valores numéricos de laboratorio en el payload.
- No se aceptan diagnósticos ni etiquetas clínicas explícitas.
- No se aceptan campos adicionales fuera de este esquema.

## 2) Esquema de salida (JSON)

**Formato esperado** (solo el cuerpo del email):

```json
{
  "email_body": "Hola Juan, queremos invitarle..."
}
```

### 2.1 Reglas de validación de salida
- `email_body`: string en español formal (usted/su).
- Longitud objetivo: 120–220 palabras (sin disclaimer).
- Debe seguir la estructura obligatoria de 7 bloques.
- No debe incluir disclaimer, firma ni links (se agregan fuera del modelo).


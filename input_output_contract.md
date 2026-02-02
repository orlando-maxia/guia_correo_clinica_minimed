# Contrato de entrada/salida del generador (v1)

Este contrato formaliza el esquema de datos permitido para invocar el generador y el formato esperado de salida. Su finalidad es evitar que el modelo invente datos fuera de la guía.

## 1) Esquema de entrada (JSON)

**Campos permitidos** (solo estos pueden ser provistos al generador):

```json
{
  "patient": {
    "patient_id": "INT-000123",
    "patient_name": "Juan",
    "patient_email": "juan@email.com"
  },
  "clinical": {
    "mdls_calculable": true,
    "mdls_score": 0.62,
    "mdls_tier": "MEDIO",
    "biomarkers": {
      "GLU": 0,
      "HBA1C": 0,
      "LDL": 0,
      "HDL": 0,
      "VLDL": 0,
      "TG": 0,
      "PLT": 0,
      "HGB": 0,
      "ALT": 0
    },
    "biomarker_flags": {
      "GLU": "NORMAL",
      "HBA1C": "SIN_DATO",
      "LDL": "FUERA_RANGO"
    },
    "mdls_derivatives": {
      "TG_HDL_RATIO": 0,
      "AST_ALT_RATIO": 0,
      "NON_HDL": 0
    },
    "comorbidity_channels": {
      "CREAT": 0,
      "FIB4": 0
    }
  },
  "temporal": {
    "last_exam_date": "2024-05-17",
    "days_since_last_exam": 120,
    "recency_type": "HISTORICO"
  }
}
```

### 1.1 Reglas de validación (administrativas)
- `patient.patient_id`: string | number, opcional, **no** se expone al paciente.
- `patient.patient_name`: string no vacío.
- `patient.patient_email`: string, solo para envío, **no** se usa en el cuerpo.

### 1.2 Reglas de validación (clínicas, uso interno)
- `clinical.mdls_calculable`: boolean.
- `clinical.mdls_score`: number, opcional (solo si `mdls_calculable = true`).
- `clinical.mdls_tier`: enum `BAJO | MEDIO | ALTO` (obligatorio si `mdls_calculable = true`).
- `clinical.biomarkers`: mapa opcional de biomarcadores MDLS (9 posibles). Valores numéricos **no se muestran** al paciente.
- `clinical.biomarker_flags`: mapa opcional con `NORMAL | FUERA_RANGO | SIN_DATO`.
- `clinical.mdls_derivatives`: mapa opcional (p. ej., `TG_HDL_RATIO`, `AST_ALT_RATIO`, `NON_HDL`).
- `clinical.comorbidity_channels`: mapa opcional (p. ej., `CREAT`, `FIB4`).

### 1.3 Reglas de validación (temporales)
- `temporal.last_exam_date`: string fecha (YYYY-MM-DD).
- `temporal.days_since_last_exam`: integer >= 0.
- `temporal.recency_type`: enum `PRIMER_EXAMEN | HISTORICO`.

### 1.4 Restricciones del esquema
- No se aceptan diagnósticos ni etiquetas clínicas explícitas.
- No se aceptan campos adicionales fuera de este esquema.
- Aunque se reciben datos clínicos, **ningún** biomarcador, score, flag o comorbilidad puede aparecer en el cuerpo del email.

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

## 3) Ejemplos mínimos de payload

### 3.1 Caso con MDLS calculable
```json
{
  "patient": {
    "patient_name": "Ana"
  },
  "clinical": {
    "mdls_calculable": true,
    "mdls_tier": "ALTO"
  },
  "temporal": {
    "days_since_last_exam": 40,
    "recency_type": "HISTORICO"
  }
}
```

### 3.2 Caso sin MDLS (solo biomarcadores disponibles)
```json
{
  "patient": {
    "patient_name": "Luis"
  },
  "clinical": {
    "mdls_calculable": false,
    "biomarker_flags": {
      "GLU": "FUERA_RANGO",
      "TG": "FUERA_RANGO"
    }
  },
  "temporal": {
    "days_since_last_exam": 380,
    "recency_type": "HISTORICO"
  }
}
```

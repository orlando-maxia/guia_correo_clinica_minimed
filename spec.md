# Spec técnica: Generador de correos Minimed (v1)

Este documento traduce la ficha técnica (`guia_v1.md`) a una especificación implementable para el generador de correos. Su objetivo es servir como contrato técnico entre data, producto e ingeniería.

## 1) Objetivo y alcance
- **Propósito:** generar correos preventivos, accesibles y no alarmistas que inviten al paciente a conocer e integrarse voluntariamente al programa de Minimed.
- **Canal permitido:** exclusivamente correo electrónico.
- **Destinatarios válidos:** pacientes con exámenes disponibles que permitan MDLS o biomarcadores asociados; potenciales beneficiarios del programa.
- **Límites:** no diagnosticar, no emitir urgencias, no comunicar resultados clínicos.

## 2) Inputs permitidos
### 2.1 Administrativos
- `patient_name` (string): nombre para saludo.
- `patient_email` (string): solo para envío, **no** se usa en el cuerpo.
- `patient_id` (string|number, opcional): trazabilidad interna, **no** se expone.

### 2.2 Clínicos (uso interno, no visibles)
- `mdls_calculable` (boolean)
- `mdls_score` (float)
- `mdls_tier` ("BAJO" | "MEDIO" | "ALTO")
- `biomarkers` (mapa de biomarcadores MDLS disponibles, valores numéricos)
- `biomarker_flags` ("NORMAL" | "FUERA_RANGO" | "SIN_DATO")
- `mdls_derivatives` (p. ej., `TG_HDL_RATIO`, `AST_ALT_RATIO`, `NON_HDL`)
- `comorbidity_channels` (p. ej., `CREAT`, `FIB4`) — solo para modulación interna

### 2.3 Temporales
- `last_exam_date` (YYYY-MM-DD)
- `days_since_last_exam` (int)
- `recency_type` ("PRIMER_EXAMEN" | "HISTORICO")

## 3) Lógica interna de segmentación
### 3.1 Regla principal
- Si `mdls_calculable = true`, asignar paquete base por `mdls_tier`:
  - `BAJO` → **STANDARD**
  - `MEDIO` → **SILVER**
  - `ALTO` → **GOLD**

### 3.2 Cuando MDLS no es calculable
- Derivar `biomarker_risk_tier` desde biomarcadores disponibles y/o comorbilidades.
- Asignar paquete:
  - `biomarker_risk_tier = BAJO` → **STANDARD**
  - `biomarker_risk_tier = MEDIO` → **SILVER**
  - `biomarker_risk_tier = ALTO` → **GOLD**

### 3.3 Ajuste por recencia (solo tono)
- La recencia **no cambia** el paquete cuando el riesgo es MEDIO/ALTO.
- Sí ajusta narrativa (p. ej., “buen momento para reforzar” vs “retomar acompañamiento”).

### 3.4 Perfiles plausibles (resumen para `biomarker_risk_tier`)
- **ALTO:** patrones coherentes de disglucemia + dislipidemia, perfil hepato‑metabólico o renal‑metabólico.
- **MEDIO:** dislipidemia aterogénica o disglucemia predominante con soporte.
- **BAJO:** alteraciones aisladas o parciales sin patrón consistente.

## 4) Estructura del email (obligatoria)
El cuerpo del correo generado debe seguir **exactamente** estos 7 bloques:
1. Apertura empática y neutral (saludo personalizable).
2. Invitación general al cuidado de la salud.
3. Presentación del programa como apoyo (no tratamiento).
4. Descripción general del acompañamiento ofrecido.
5. Enfoque motivacional y de tranquilidad.
6. CTA simple y no agresivo.
7. Cierre institucional + disclaimer (insertado por plantilla del sistema).

## 5) Personalización permitida
**Solo se permite variar:**
- Saludo con `patient_name`.
- Enfoque general según paquete (Standard/Silver/Gold).
- Beneficios descritos (sin tecnicismos).
- Narrativa temporal (primer contacto vs retomar seguimiento).
- CTA (agendar, responder, solicitar info).

**No personalizable:** estructura, tono preventivo, disclaimer, firma institucional, enlaces y canales oficiales.

## 6) Estilo base por paquete + variabilidad controlada
El LLM debe generar el cuerpo del email con el estilo, tono y enfoque del paquete asignado (Standard/Silver/Gold), usando las plantillas base como referencia semántica.

El modelo no debe copiar literal, pero sí conservar el mismo tipo de mensaje, nivel de acompañamiento y CTA.

## 7) Inputs narrativos permitidos (LLM)
Para personalización narrativa, el LLM solo puede usar los siguientes campos:

```json
{
  "narrative_inputs": {
    "recency_type": "PRIMER_EXAMEN | HISTORICO",
    "days_since_last_exam": 120,
    "package": "STANDARD | SILVER | GOLD",
    "program_name": "Programa Minimed"
  }
}
```

Estos inputs no exponen biomarcadores ni datos clínicos sensibles, y delimitan qué información puede aparecer en el texto.

## 8) Prompt Contract (obligatorio)
Reglas del contrato para la generación del cuerpo del email:

- Estructura obligatoria de 7 bloques.
- Longitud 120–220 palabras (sin disclaimer).
- No mencionar resultados, biomarcadores ni términos prohibidos.
- Tono preventivo, no alarmista.
- Personalización permitida solo con:
  - `patient_name`
  - `recency_type` / `days_since_last_exam`
  - `package`
  - beneficios generales del plan

## 9) Biblioteca de ejemplos ancla por paquete
Las plantillas base funcionan como **anchor exemplars** de estilo, no como outputs fijos.

- STANDARD → prevención general.
- SILVER → acompañamiento más activo.
- GOLD → programa integral.

El LLM debe parecerse en tono y enfoque a estos ejemplos, pero con variaciones de wording y énfasis según recencia y paquete.

## 10) Restricciones (guardrails)
- No mencionar MDLS, biomarcadores, valores de laboratorio ni fechas específicas de examen.
- No diagnosticar ni inferir síntomas, tratamientos o complicaciones.
- No usar lenguaje de alarma, culpa o urgencia.
- No prometer resultados clínicos.

## 11) Output esperado
- **Salida del generador:** solo el **cuerpo del email** (texto principal).
- **Idioma:** español formal (usted/su).
- **Longitud:** 120–220 palabras (sin disclaimer).
- **Excluye:** firma institucional, disclaimer legal, links, teléfono y opción de baja (se agregan por plantilla externa).

## 12) Campos institucionales (fuera del modelo)
Insertados por sistema de plantillas:
- Nombre oficial de la clínica y del programa.
- Nombres de planes (Standard, Silver, Gold).
- Link de agenda o contacto principal.
- Teléfono y correo institucional.
- Firma fija.
- Disclaimer legal y opción de baja.

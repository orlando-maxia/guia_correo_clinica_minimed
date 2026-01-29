# Ficha técnica para la generación de correos electrónicos personalizados con IA para adherencia al Programa de Diabetes de Minimed

Versión

Fecha

Dirección Ciencia de Datos y Analitica

Uso previsto

# Objetivo del generador de correos electrónicos

Propósito técnico: Definir la intención global que debe guiar todas las decisiones del modelo de IA al generar correos personalizados. Establece qué busca lograr el sistema a nivel comunicacional y operativo.

## 1.1 Objetivo primario del mensaje

Generar un correo electrónico que invite al paciente a interesarse por su salud metabólica e integrarse voluntariamente al programa de control y acompañamiento ofrecido por Minimed, mediante una comunicación preventiva, accesible y no alarmista.

## 1.2 Objetivos secundarios

- Promover la participación temprana de pacientes y el seguimiento general en salud, sin comunicar resultados clínicos específicos.
- Incrementar la confianza del paciente en el programa de diabetes de Minimed como una opción de apoyo y acompañamiento médico.
- Mantener coherencia institucional y consistencia comunicacional en todos los mensajes generados.
- Permitir escalabilidad del sistema para personalización futura con nuevas variables clínicas autorizadas.

## 1.3 Resultados esperados

El modelo se considera exitoso si el correo generado produce algunos de los siguientes resultados:

- el paciente muestra interés en conocer el programa
- el paciente responde solicitando información
- el paciente agenda un contacto o evaluación inicial
- el paciente percibe el mensaje como una invitación de bienestar, no como una alerta médica

# Alcance y contexto de uso

Propósito técnico: Delimitar el uso correcto del generador para evitar aplicaciones indebidas, garantizar consistencia clínica y asegurar que el sistema opere dentro de un marco ético y normativo.

## 2.1 Canal permitido

El generador está diseñado exclusivamente para comunicación por **correo electrónico**. No debe utilizarse para:

- mensajes SMS
- llamadas automatizadas
- notificaciones clínicas urgentes
- comunicación en emergencias

## 2.2 Tipo de destinatarios

Los correos generados están dirigidos únicamente a:

- pacientes que cuentan con exámenes de laboratorio con al menos un biomarcador del MDLS disponible (puede ser distinto de HbA1c) y/o con MDLS calculable
- pacientes potencialmente beneficiarios del Programa de Diabetes

El sistema no está diseñado para:

- población general sin antecedentes
- pacientes en contexto de urgencia médica
- comunicación pediátrica o poblaciones especiales sin adaptación clínica

## 2.3 Contexto clínico general

El mensaje se enmarca dentro de un programa institucional de control y seguimiento en salud metabólica. Su finalidad es:

- invitar al acompañamiento preventivo
- facilitar acceso a planes estructurados de bienestar y control
- El mensaje no constituye una comunicación diagnóstica.

## 2.4 Limitaciones del mensaje

El correo generado por el modelo:

- no reemplaza una consulta médica
- no equivale a un diagnóstico
- no debe interpretarse como indicación terapéutica
- no funciona como alerta clínica ni urgencia sanitaria
- Cualquier evaluación individual requiere atención profesional directa.

# Variables de entrada (inputs)

Propósito técnico: Definir qué datos puede usar el modelo y cuáles no, para generar correos personalizados dirigidos a pacientes del programa de control y seguimiento de diabetes. El modelo solo puede usar explícitamente las variables declaradas en esta sección, y no puede inferir síntomas, diagnósticos, complicaciones ni tratamientos.

Estas variables cumplen tres funciones:

- Identificar al paciente dentro del sistema
- Interpretar su estado clínico actual de forma no diagnóstica
- Adaptar el mensaje en tono, urgencia y recomendación del programa

## Variables administrativas

Estas variables permiten que el mensaje será enviado correctamente y mantenga un nivel básico de personalización, sin implicaciones clínicas.

| **Variable** | **Tipo** | **Descripción** | **Uso permitido** | **Restricción** |
| --- | --- | --- | --- | --- |
| Nombre del paciente | Texto (string) | Nombre utilizado para saludo inicial en el correo. | Personalización superficial (ej. "Hola Juan"). | No usar diminutivos ni lenguaje excesivamente informal. |
| Correo electrónico | Texto (string) | Dirección de contacto del paciente, canal único disponible actualmente. | Uso exclusivo para envío del mensaje. | No debe aparecer explícitamente dentro del cuerpo del correo. |
| Identificador interno del paciente (opcional) | Texto o numérico | Clave interna para trazabilidad y control del sistema. | Ninguno dentro del mensaje (solo backend). | Nunca debe ser expuesto al paciente. |

## 3.2 Variables clínicas

Representan la información médica disponible para personalizar el contenido del mensaje.

| **Variable** | **Tipo** | **Descripción** | **Uso permitido** | **Restricción** |
| --- | --- | --- | --- | --- |
| MDLS_calculable | Booleano | Indica si el MDLS puede calcularse con la data disponible. | Elegir flujo de interpretación (MDLS vs biomarcadores individuales). | No se comunica al paciente. |
| MDLS_score | Numérico (float) | Puntaje continuo de desregulación metabólica (si MDLS_calculable = true). | Base para segmentación interna del paquete. | No se comunica ni se menciona "MDLS". |
| MDLS_tier | Categórica (BAJO / MEDIO / ALTO) | Banda interna derivada del MDLS_score. | Seleccionar paquete y tono. | No se comunica al paciente. |
| Biomarcadores MDLS (9) | Numérico (float) por biomarcador | Valores disponibles de los biomarcadores del MDLS (p. ej., GLU, HBA1C, LDL, HDL, VLDL, TG, PLT, HGB, ALT; ver catálogo interno). | Apoyar segmentación cuando MDLS no es calculable o hay datos parciales. | No se comunica el nombre ni el valor del biomarcador. |
| Flags por biomarcador | Categórica (NORMAL / FUERA_RANGO / SIN_DATO) | Estado clínico por biomarcador según reglas clínicas internas. | Determinar nivel de riesgo interno cuando no hay MDLS, incluso con datos parciales. | No se comunica al paciente. |
| Derivadas MDLS | Numérico (float) | Ratios/derivadas internas (TG_HDL_RATIO, AST_ALT_RATIO, NON_HDL). | Ajuste fino del riesgo interno. | No se comunica. |
| Canales de comorbilidad | Numérico (float) | CREAT y FIB-4 si están disponibles. | Solo como modulación interna (no diagnóstica). | No se comunican. |

## 3.3 Variables temporales

Permiten modular el mensaje según la recencia del seguimiento, lo cual afecta la urgencia narrativa pero no implica diagnóstico.

| **Variable** | **Tipo** | **Descripción** | **Uso permitido** | **Restricción** |
| --- | --- | --- | --- | --- |
| Fecha del último examen disponible | Fecha (YYYY-MM-DD) | Fecha más reciente de cualquier biomarcador MDLS registrado. | Referencias temporales neutras ("en su examen reciente…"). | No usar para generar culpa o reproche. |
| Días desde el último examen disponible | Numérico entero | Diferencia entre fecha actual y la fecha más reciente de biomarcadores MDLS. | Ajustar urgencia narrativa ("ha pasado un tiempo desde…"). | No debe interpretarse como abandono médico ni negligencia. |
| Tipo de recencia del paciente | Categórica (PRIMER_EXAMEN / HISTORICO) | Indica si es el primer resultado registrado o un seguimiento previo. | Seleccionar línea narrativa coherente ("primer resultado" vs "última medición"). | Evitar contradicciones temporales dentro del mensaje. |

# Marco de interpretación de variables

Propósito técnico: Traducir datos crudos en significado comunicacional, no diagnóstico. El MDLS y los biomarcadores asociados se usan solo para definir un nivel de acompañamiento interno y un tono preventivo, sin comunicar resultados ni motivos clínicos específicos.

El paciente nunca debe sentir que el correo es una alerta médica, por ende:

- MDLS y biomarcadores son invisibles en el discurso
- No se menciona "rango", "elevado", "necesidad"
- El correo se posiciona como invitación preventiva

## 4.1 Interpretacion (interna) de MDLS y biomarcadores

Tabla de uso interno para la interpretacion de MDLS y biomarcadores, que debe utilizarse unicamente para seleccionar el tipo de mensaje y el programa ofrecido:

- MDLS_tier define el paquete base (Standard / Silver / Gold) cuando MDLS_calculable = true
- La recencia NO cambia el paquete en niveles altos, solo ajusta el tono
- Si MDLS_calculable = false, se usa el riesgo derivado de biomarcadores disponibles (biomarker_risk_tier)
- Si solo existe data de un biomarcador, NO se calcula MDLS, pero si hay riesgo potencial se puede asignar Silver segun biomarker_risk_tier, aun si el biomarcador no es HbA1c
- Si el único biomarcador disponible indica riesgo potencial de diabetes y/o desregulacion metabolica, se prioriza un mensaje preventivo con acompanamiento (sin explicitar el motivo)

| **Condicion interna** | **Recencia del ultimo examen** | **Paquete asignado (interno)** | **Urgencia narrativa interna** | **Enfoque del discurso comercial** |
| --- | --- | --- | --- | --- |
| MDLS_tier = ALTO | Cualquier recencia | GOLD | Alta prioridad | Invitacion a plan integral y completo de acompanamiento |
| MDLS_tier = MEDIO | < 90 dias | SILVER | Intervencion oportuna | "Momento ideal para reforzar control y bienestar" |
| MDLS_tier = MEDIO | >= 90 dias | SILVER | Seguimiento atrasado | "Retomar acompanamiento puede marcar diferencia" |
| MDLS_tier = BAJO | > 365 dias | STANDARD | Seguimiento general pendiente | "Invitacion a chequeo preventivo y acompanamiento" |
| MDLS_tier = BAJO | <= 365 dias | STANDARD | Prevencion activa | "Programa inicial para habitos y control temprano" |
| MDLS_calculable = false AND biomarker_risk_tier = ALTO | Cualquier recencia | SILVER | Intervencion oportuna | "Acompanamiento mas estructurado para cuidar su salud" |
| MDLS_calculable = false AND biomarker_risk_tier = MEDIO | Cualquier recencia | STANDARD | Prevencion temprana | "Etapa ideal para prevenir desregulacion metabolica" |
| MDLS_calculable = false AND biomarker_risk_tier = BAJO | > 365 dias | STANDARD (bienestar general) | Baja urgencia | "Programa de salud metabolica y control periodico" |

## 4.2 Prohibicion explicita de comunicacion del examen

- Mencionar porcentaje exacto
- Referirse al MDLS o a biomarcadores como indicador de riesgo
- "dar seguimiento a su resultado" o "dar seguimiento a su score"

| **Prohibido** | **Ejemplos** |
| --- | --- |
| Diagnóstico directo | "Usted tiene diabetes." |
| Afirmación de gravedad | "Su caso es grave." |
| Predicción clínica | "Va a desarrollar complicaciones." |
| Suposición de síntomas | "Seguramente tiene daño renal." |
| Culpa o reproche | "Usted no se ha cuidado." |

## 4.3 Traducción narrativa externa - tipo de lenguaje habilitado

El paciente nunca ve nombres de biomarcadores ni el "MDLS", ni "rango", ni palabras como "seguimiento necesario", sino que recibe una invitación de bienestar adaptada. En la siguiente tabla se muestra un ejemplo de de la adaptación narrativa según el principio rector:

- Los biomarcadores del MDLS son indicadores de salud metabolica, no diagnosticos automaticos.
- El correo debe invitar al seguimiento, no etiquetar clinicamente al paciente.

| **Paquete interno** | **Condición interna (uso sistema)** | **Apertura recomendada (neutral)** | **Enfoque del mensaje** | **\*CTA sugerido** |
| --- | --- | --- | --- | --- |
| STANDARD | MDLS_tier = BAJO con recencia ≤365d | "Queremos invitarle a un programa pensado para cuidar su salud desde etapas tempranas." | Prevención, hábitos, acompañamiento inicial | "Conozca el Plan Standard" |
| STANDARD | MDLS_tier = BAJO con recencia >365d o biomarker_risk_tier = MEDIO | "Un chequeo periódico es una gran herramienta para mantenerse en equilibrio." | Bienestar general y monitoreo preventivo | "Agende una evaluación de rutina" |
| SILVER | MDLS_tier = MEDIO con examen reciente | "Este puede ser un buen momento para fortalecer su bienestar y seguimiento médico." | Control activo, apoyo más frecuente | "Conozca el Plan Silver" |
| SILVER | MDLS_tier = MEDIO con recencia >90d o biomarker_risk_tier = ALTO | "Retomar un acompañamiento médico estructurado puede ayudarle a sentirse mejor y más tranquilo." | Reenganche sin culpa, continuidad | "Agende una llamada de orientación" |
| SILVER | MDLS_calculable = false con un solo biomarcador fuera de rango | "A veces, contar con un plan más completo facilita mantener constancia y control." | Estructura adicional, seguimiento más regular | "Explore el Plan Silver" |
| GOLD | MDLS_tier = ALTO cualquier recencia | "Contamos con un programa integral diseñado para brindarle un acompañamiento completo en su salud." | Evaluación amplia, apoyo multidisciplinario sin alarmar | "Conozca el Plan Gold" |

\*CTA: _Call To Action_, "Llamada a la acción".

# 5\. Reglas de composición del mensaje

Propósito técnico: Esta sección define la estructura mínima obligatoria que debe seguir cualquier correo generado por el modelo de IA, es decir, define el orden lógico y los componentes comunicacionales obligatorios. En este sentido, el mensaje debe ser interpretado por el paciente como "una invitación preventiva y accesible a un programa de bienestar y acompañamiento médico".

## 5.1 Estructura mínima obligatoria del correo

Un correo generado se considera válido si cumple:

- contiene los 7 componentes obligatorios (que se describen más abajo)
- no menciona valores clínicos
- no genera alarma
- mantiene tono preventivo y voluntario
- incluye CTA (_call to action_)claro y disclaimer final

Todo mensaje generado debe contener los siguientes 7 bloques o compenentes, en este orden:

### 5.1.1 Apertura empática y neutral

**Función:** iniciar el correo de forma humana, respetuosa y no invasiva.

Características:

- saludo personalizado permitido
- tono calmado
- sin referencia a resultados clínicos

Ejemplo funcional: "apertura de contacto desde Minimed con intención preventiva"

### 5.1.2 Invitación general al cuidado de la salud

**Función:** contextualizar el mensaje como una acción de bienestar, no de alarma.

Debe comunicar:

- interés en acompañar
- oportunidad de autocuidado
- prevención como enfoque principal

### 5.1.3 Presentación del programa como apoyo (no como tratamiento)

**Función:** introducir el programa como una opción voluntaria de acompañamiento.

Debe incluir:

- que existe un programa de control y seguimiento
- que está diseñado para apoyar al paciente en su salud metabólica

### 5.1.4 Descripción general del tipo de acompañamiento ofrecido

**Función:** explicar beneficios del programa sin entrar en tecnicismos ni especialidades innecesarias.

Puede mencionar:

- seguimiento médico
- nutrición
- hábitos
- monitoreo general

### 5.1.5 Enfoque motivacional y de tranquilidad

**Función:** reforzar que el programa es una oportunidad positiva.

El mensaje debe transmitir:

- acompañamiento
- accesibilidad
- control como algo alcanzable

### 5.1.6 Llamado a la acción simple y no agresivo (CTA)

**Función:** permitir que el paciente avance fácilmente si tiene interés.

Debe ofrecer una acción concreta:

- agendar
- responder
- solicitar información

Características:

- opcionalidad explícita
- tono invitacional, no prescriptivo

Ejemplo funcional: "Si desea conocer más, puede agendar una llamada…"

### 5.1.7 Cierre institucional + disclaimer obligatorio

**Función:** cerrar profesionalmente y cumplir requisitos éticos.

Debe incluir:

- firma de la clínica
- canal de contacto
- nota de que no sustituye consulta médica
- opción de baja de comunicaciones

# Parámetros de personalización permitida

Propósito técnico: Definir los elementos del correo electrónico que el modelo de IA puede adaptar entre pacientes para generar mensajes personalizados, sin comprometer:

- consistencia estructural,
- neutralidad clínica,
- ni percepción de alerta médica.

La personalización se entiende como variación controlada del contenido dentro de límites comunicacionales seguros.

Un mensaje personalizado se considera válido si:

- mantiene la estructura definida en Sección 5
- adapta únicamente los componentes autorizados
- no revela lógica interna de segmentación
- conserva tono neutral y voluntario.

## 6.1 Componentes personalizables del mensaje

El modelo puede modificar únicamente los siguientes elementos:

| **Componente** | **Fuente** | **Tipo de personalización permitida** |
| --- | --- | --- |
| Saludo inicial | Nombre del paciente | Inserción nominal simple ("Hola {Nombre}") |
| Enfoque general del mensaje | Nivel de programa asignado internamente | Prevención / acompañamiento activo / programa integral |
| Beneficios descritos | Paquete ofrecido | Selección proporcional de servicios (sin tecnicismos excesivos) |
| Línea narrativa de recencia | Tipo de recencia (primer contacto vs seguimiento) | Ajuste leve del framing ("inicio" vs "retomar") |
| Llamado a la acción (CTA) | Canales disponibles | Agendar / responder / solicitar información |

## 6.2 Elementos NO personalizables (deben permanecer constantes)

Los siguientes componentes deben mantenerse fijos para todos los pacientes:

| **Elemento** | **Razón técnica** |
| --- | --- |
| Disclaimer legal final | Cumplimiento normativo |
| Tono preventivo y no alarmista | Consistencia comunicacional |
| Estructura de 7 bloques obligatorios | Validación del sistema |
| Presentación institucional del programa | Confianza y claridad |

## 6.3 Grado máximo de personalización permitido

El sistema debe evitar personalización excesiva.

Se permite:

- adaptación de enfoque general,
- selección de beneficios,
- ajuste leve de narrativa temporal.

No se permite:

- hiperpersonalización clínica,
- referencias implícitas a resultados,
- lenguaje que sugiera conocimiento íntimo del estado del paciente.

## 6.4 Personalización temporal permitida

La variable temporal solo puede reflejarse como framing narrativo general:

| **Situación** | **Enfoque permitido** |
| --- | --- |
| Primer contacto | "Queremos compartirle este programa desde el inicio…" |
| Seguimiento previo | "Le invitamos a retomar opciones de acompañamiento…" |

# Lineamientos de tono y estilo

Propósito técnico: Esta sección regula únicamente cómo se lleva a cabo la redacción del mensaje, es decir, aquí se definirán las reglas de estilo lingüístico que debe seguir el modelo de IA al redactar los correos, garantizando consistencia editorial, claridad y alineación con la identidad comunicacional de Minimed.

Un correo cumple esta sección si:

- mantiene registro formal consistente
- utiliza vocabulario recomendado
- evita lenguaje de alerta o culpa
- no emplea marketing agresivo
- es claro y fácil de leer

Regla que rige esta sección: El modelo solo genera el contenido narrativo del mensaje. Los campos institucionales anteriores deben ser añadidos mediante plantillas controladas por el sistema.

## 7.1 Registro y tratamiento

- Tratamiento estándar: "usted / su"
- Evitar alternancia de registro (no mezclar "usted" con "tú").
- Saludos y cierres deben mantenerse sobrios e institucionales.

## 7.2 Diccionario de lenguaje recomendado

El modelo debe priorizar vocabulario centrado en bienestar y acompañamiento:

- "cuidar su salud"
- "acompañamiento"
- "programa" / "plan"
- "orientación"
- "hábitos saludables"
- "seguimiento general"
- "tranquilidad" / "respaldo"

## 7.3 Lenguaje a evitar (carga de alerta o juicio)

Evitar términos que puedan percibirse como alarmantes o evaluativos:

- "grave", "peligroso", "urgente"
- "complicaciones", "daño", "deterioro"
- "usted necesita", "usted requiere", "debe atenderse"
- cualquier formulación que implique reproche o culpa

## 7.4 Estilo persuasivo permitido (sin marketing agresivo)

La persuasión debe basarse en:

- Claridad del beneficio: El mensaje puede destacar de forma sencilla qué aporta el programa al paciente (acompañamiento, orientación, seguimiento general), sin prometer resultados médicos específicos.
- Accesibilidad del programa: Se puede enfatizar que el programa está diseñado para ser una opción cercana, disponible y fácil de aprovechar, transmitiendo apoyo y acompañamiento, no urgencia.
- Facilidad de contacto: El correo debe hacer evidente que el siguiente paso es simple (agendar, responder, pedir información), reduciendo fricción y manteniendo voluntariedad.

No se permite:

- Lenguaje promocional exagerado: Evitar expresiones propias de publicidad ("oferta imperdible", "aproveche ya"), ya que disminuyen credibilidad clínica y pueden generar rechazo.
- Urgencia artificial ("últimos cupos", "solo hoy"): No se deben usar técnicas de presión temporal, porque el programa es un servicio de salud, no una venta impulsiva.
- Promesas clínicas ("mejorará en X tiempo"): El modelo no puede garantizar resultados médicos ni plazos de mejora, ya que cada caso requiere evaluación profesional y esto podría implicar riesgo ético y legal.

## 7.5 Reglas de legibilidad y formato

- Longitud recomendada: 120-220 palabras (sin disclaimer).
- Oraciones cortas y directas.
- Párrafos breves (máx. 3 líneas).
- Listas de beneficios: máximo 4-6 bullets.
- Evitar tecnicismos clínicos.

## 7.6 Consistencia institucional

Para garantizar consistencia institucional y reducir variabilidad no deseada, ciertos elementos del correo deben ser tratados como campos fijos o plantillas no generativas. Estos componentes no deben ser redactados libremente por el modelo, sino insertados automáticamente desde el sistema:

| **Campo institucional** | **Tipo** | **Fuente** | **Regla de uso** |
| --- | --- | --- | --- |
| Nombre oficial de la clínica | Texto fijo | Configuración institucional | No permitir variaciones ("Minimed" debe ser único). |
| Nombre oficial del programa | Texto fijo | Catálogo interno | No inventar sinónimos ("programa de control metabólico" vs "programa diabetes"). |
| Nombre de planes disponibles | Lista fija | Catálogo comercial | Solo se permiten: Standard, Silver, Gold. |
| Link de agenda o contacto principal | Variable estructurada | Sistema (CRM / calendario) | Debe aparecer siempre en el bloque CTA. |
| Teléfono oficial de contacto | Texto fijo | Configuración institucional | No generar números ni formatos alternativos. |
| Correo de respuesta institucional | Texto fijo | Configuración institucional | No usar correos distintos. |
| Firma institucional final | Plantilla fija | Clínica | Debe mantenerse idéntica en todos los correos. |
| Disclaimer legal obligatorio | Plantilla fija | Área legal/compliance | No debe ser reescrito por IA. Debe insertarse completo. |
| Opción de baja ("unsubscribe") | Plantilla fija | Política institucional | Debe incluirse siempre como texto estándar. |

# Límites éticos, clínicos y legales

Propósito técnico: Definir las restricciones no negociables que rigen el comportamiento del modelo de IA. Estas reglas operan como guardrails de seguridad clínica, ética y legal, y deben cumplirse en todos los correos generados, independientemente del nivel del programa ofrecido.

| **Límite** | **Regla no negociable** | **Ejemplos prohibidos** |
| --- | --- | --- |
| Prohibición de diagnóstico automatizado | El modelo no puede diagnosticar, confirmar enfermedades ni sustituir una consulta médica. | "Usted tiene diabetes" / "Esto confirma un problema clínico" |
| Restricción de inferencia clínica | El modelo no puede asumir ni mencionar síntomas, tratamientos, complicaciones o antecedentes no disponibles en las variables de entrada. | "Necesita insulina" / "Tiene daño renal" |
| Prohibición de comunicación de información clínica sensible | El modelo no debe comunicar resultados médicos específicos como motivo del contacto. | Mencionar valores de biomarcadores o MDLS / Fechas de exámenes / "Le escribimos por su resultado" |
| Disclaimer obligatorio y voluntariedad | Todo correo debe incluir el disclaimer institucional fijo: no es diagnóstico, no reemplaza consulta médica, participación voluntaria y opción de baja. | Omitir disclaimer / Presentar el programa como obligatorio |

En consecuencia, un correo cumple esta sección si:

- no contiene diagnósticos ni afirmaciones médicas concluyentes
- no incluye inferencias clínicas no disponibles en los datos de entrada
- no comunica resultados de laboratorio ni información clínica sensible
- no emite recomendaciones terapéuticas específicas
- incluye siempre el disclaimer institucional fijo y respeta la voluntariedad del paciente

# Output esperado (definición funcional)

Propósito técnico: Definir con precisión el tipo de salida que debe producir el modelo de IA al ejecutarse, para su integración, validación y despliegue como componente dentro del sistema de envío de correos.

- Tipo de salida**:** El modelo debe retornar como output un bloque de texto en formato email, correspondiente al cuerpo principal del mensaje.
  - El output debe ser directamente utilizable en un sistema de mensajería (CRM, plataforma de email o automatización interna).
- Formato del contenido generado: El contenido generado debe estar compuesto por texto continuo estructurado en párrafos breves, e incluir de forma natural:
  - saludo inicial (si aplica)
  - invitación al programa
  - descripción general del acompañamiento ofrecido
  - llamado a la acción (CTA)
- Idioma y registro: El output debe generarse en:
  - español
  - registro formal consistente (uso de "usted")
- Longitud esperada: El texto generado debe tener una extensión aproximada de:
  - 120 a 220 palabras
  - Esto excluye componentes institucionales insertados externamente (ver Sección 7.6).
- Componentes fuera del alcance del modelo: El modelo no debe generar los siguientes elementos, ya que son añadidos mediante plantillas fijas del sistema (ver Sección 8):
  - disclaimer legal obligatorio
  - firma institucional estándar
  - links oficiales y datos de contacto estructurados
  - opción de baja de comunicaciones
- Salida esperada para integración técnica: El modelo debe devolver únicamente el texto principal del correo (cuerpo del mensaje), en un solo bloque listo para ser insertado por el sistema de envío, por ejemplo:
  - email_body (o el nombre de campo de su preferencia)
  - No debe incluir metadata adicional, diagnósticos, resultados clínicos ni identificadores internos.

# Versionamiento y evolución futura

Propósito técnico: Definir cómo debe mantenerse y actualizarse esta ficha técnica a medida que se incorporen nuevas variables clínicas, operativas o de segmentación, garantizando que el sistema de generación de correos permanezca consistente, seguro y compatible.

## 10.1 Principio de extensibilidad

Esta guía está diseñada para evolucionar desde un modelo multivariable basado en MDLS hacia un modelo enriquecido con otras variables. Nuevas variables potenciales incluyen:

- edad
- IMC
- presión arterial
- historial longitudinal de biomarcadores disponibles
- comorbilidades registradas
- otros perfiles (lipídico, hepático, etc.)
- frecuencia de controles, entre otros.

## 10.2 Regla de incorporación de nuevas variables

Toda nueva variable integrada al sistema debe añadirse formalmente en:

- Sección 4: Variables de entrada permitidas
- Sección 5: Marco de interpretación interna
- Sección 6: Parámetros de personalización permitida (si aplica)
- Sección 8: Límites clínicos y privacidad asociados

Ninguna variable puede ser utilizada por el modelo si no está documentada explícitamente.

## 10.3 Compatibilidad hacia atrás

Las futuras versiones del modelo deben mantener funcionalidad mínima con el set actual de variables. Esto implica que:

- el sistema debe seguir operando correctamente si solo existe data de un biomarcador del MDLS
- la ausencia de nuevas variables no debe generar errores ni inferencias

## 10.4 Control de versiones del documento

La ficha técnica debe mantenerse bajo versionamiento formal:

- Versión 1.0: MDLS + biomarcadores (9) + recencia
- Versión 2.0: incorporación de variables adicionales
- Versiones menores: ajustes de estilo, compliance o plantillas institucionales

Cada cambio debe registrar:

- fecha
- responsable
- variables afectadas
- impacto esperado en mensajes

## 10.5 Revalidación clínica y legal

Cada actualización relevante (nuevas variables o nuevas reglas de personalización) debe ser revisada por:

- equipo médico
- compliance/legal
- operaciones del programa

Antes de su despliegue en producción.

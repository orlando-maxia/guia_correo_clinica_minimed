"""Compliance validators for generated email content."""
from __future__ import annotations

import re
from typing import Iterable, Sequence

DEFAULT_FORBIDDEN_TERMS = (
    "hba1c",
    "glucosa",
    "biomarcador",
    "biomarcadores",
    "resultado",
    "resultados",
    "rango",
    "elevado",
    "elevada",
    "diabetes",
    "prediabetes",
)

DEFAULT_DIAGNOSIS_PATTERNS = (
    r"\busted\s+tiene\s+diabetes\b",
    r"\busted\s+padece\s+diabetes\b",
    r"\busted\s+presenta\s+diabetes\b",
    r"\bdiagnóstico\s+de\s+diabetes\b",
    r"\bdiagnosticad[oa]\s+con\s+diabetes\b",
)

DEFAULT_URGENCY_TERMS = (
    "urgente",
    "urgencia",
    "inmediato",
    "inmediatamente",
    "debe atenderse ya",
    "debe atenderse de inmediato",
)


class ComplianceError(ValueError):
    """Raised when the email body violates compliance rules."""


def validate_email(
    text: str,
    *,
    forbidden_terms: Iterable[str] = DEFAULT_FORBIDDEN_TERMS,
    diagnosis_patterns: Sequence[str] = DEFAULT_DIAGNOSIS_PATTERNS,
    urgency_terms: Iterable[str] = DEFAULT_URGENCY_TERMS,
) -> None:
    """Validate generated email content against compliance rules.

    Raises:
        ComplianceError: When a forbidden term, diagnosis, or urgency trigger is found.
    """

    violations = _collect_violations(
        text,
        forbidden_terms=forbidden_terms,
        diagnosis_patterns=diagnosis_patterns,
        urgency_terms=urgency_terms,
    )
    if violations:
        formatted = "; ".join(violations)
        raise ComplianceError(f"Contenido no permitido: {formatted}")


def _collect_violations(
    text: str,
    *,
    forbidden_terms: Iterable[str],
    diagnosis_patterns: Sequence[str],
    urgency_terms: Iterable[str],
) -> list[str]:
    lower_text = (text or "").lower()
    violations: list[str] = []

    for term in forbidden_terms:
        normalized = term.lower()
        if normalized and normalized in lower_text:
            violations.append(f"término prohibido: {term}")

    for term in urgency_terms:
        normalized = term.lower()
        if normalized and normalized in lower_text:
            violations.append(f"lenguaje de urgencia: {term}")

    for pattern in diagnosis_patterns:
        if re.search(pattern, lower_text):
            violations.append(f"diagnóstico explícito: {pattern}")

    return violations

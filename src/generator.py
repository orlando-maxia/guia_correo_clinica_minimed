"""Single-entry email generator for the Minimed preventive program."""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from .compliance import validate_email

ALLOWED_PACKAGES = {"STANDARD", "SILVER", "GOLD"}
ALLOWED_RECENCY_TYPES = {"PRIMER_EXAMEN", "HISTORICO"}

RECENCY_MESSAGES = {
    "PRIMER_EXAMEN": "Queremos darle la bienvenida y acercarle esta invitación por primera vez.",
    "HISTORICO_RECIENTE": "Este puede ser un buen momento para fortalecer su bienestar y seguimiento médico.",
    "HISTORICO_MEDIO": "Retomar un acompañamiento médico estructurado puede ayudarle a sentirse mejor y más tranquilo.",
    "HISTORICO_LARGO": "Un chequeo periódico es una gran herramienta para mantenerse en equilibrio.",
}


def build_prompt(
    patient_name: str,
    package: str,
    recency_type: str,
    days_since_last_exam: int,
    program_name: str = "Programa Preventivo de Minimed",
) -> str:
    """Build the prompt contract for the LLM, including narrative anchors."""
    normalized_package = _normalize_package(package)
    normalized_recency = _normalize_recency(recency_type)

    recency_message = build_recency_message(normalized_recency, days_since_last_exam)
    prompt_contract = _load_prompt_contract()
    anchor_template = _load_package_template(normalized_package)

    anchor_example = (
        anchor_template.replace("{{patient_name}}", patient_name).replace(
            "{{recency_message}}", recency_message
        )
    )

    return (
        f"{prompt_contract}\n\n"
        "INPUTS PARA LA GENERACIÓN\n"
        f"- patient_name: {patient_name}\n"
        f"- recency_type: {normalized_recency}\n"
        f"- days_since_last_exam: {days_since_last_exam}\n"
        f"- package: {normalized_package}\n"
        f"- program_name: {program_name}\n\n"
        "EJEMPLO DE ESTILO POR PAQUETE (NO COPIAR LITERAL)\n"
        f"{anchor_example}\n\n"
        "RESPUESTA:\n"
    )


def generate_email(
    patient_name: str,
    package: str,
    recency_type: str,
    days_since_last_exam: int,
    llm: Callable[[str], str],
    program_name: str = "Programa Preventivo de Minimed",
    validator: Callable[[str], None] | None = validate_email,
) -> str:
    """Generate the email body using a single LLM call."""
    if llm is None:
        raise ValueError("llm callable is required to generate the email")

    prompt = build_prompt(
        patient_name=patient_name,
        package=package,
        recency_type=recency_type,
        days_since_last_exam=days_since_last_exam,
        program_name=program_name,
    )
    response = llm(prompt).strip()
    if validator is not None:
        validator(response)
    return response


def build_recency_message(recency_type: str, days_since_last_exam: int) -> str:
    """Return a brief narrative line based on recency."""
    normalized_recency = _normalize_recency(recency_type)
    if normalized_recency == "PRIMER_EXAMEN":
        return RECENCY_MESSAGES["PRIMER_EXAMEN"]
    if days_since_last_exam > 365:
        return RECENCY_MESSAGES["HISTORICO_LARGO"]
    if days_since_last_exam > 90:
        return RECENCY_MESSAGES["HISTORICO_MEDIO"]
    return RECENCY_MESSAGES["HISTORICO_RECIENTE"]


def _normalize_package(package: str) -> str:
    normalized = (package or "").strip().upper()
    if normalized not in ALLOWED_PACKAGES:
        raise ValueError(f"Package must be one of {sorted(ALLOWED_PACKAGES)}")
    return normalized


def _normalize_recency(recency_type: str) -> str:
    normalized = (recency_type or "").strip().upper()
    if normalized not in ALLOWED_RECENCY_TYPES:
        raise ValueError(f"recency_type must be one of {sorted(ALLOWED_RECENCY_TYPES)}")
    return normalized


def _load_prompt_contract() -> str:
    return _read_text("prompts/email_prompt_v1.txt")


def _load_package_template(package: str) -> str:
    filename = f"templates/{package.lower()}.txt"
    return _read_text(filename)


def _read_text(relative_path: str) -> str:
    repo_root = Path(__file__).resolve().parents[1]
    return (repo_root / relative_path).read_text(encoding="utf-8").strip()

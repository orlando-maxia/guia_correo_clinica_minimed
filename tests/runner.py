"""Run deterministic validation cases for the email generator."""
from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.compliance import ComplianceError, validate_email
from src.decision_engine import DecisionInput, assign_package


def main() -> int:
    cases_path = REPO_ROOT / "tests" / "test_cases.json"
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    failures: list[str] = []

    for case in cases:
        case_id = case["id"]
        payload = case["input"]
        expected = case["expected"]

        decision_input = DecisionInput(
            mdls_calculable=payload["clinical"]["mdls_calculable"],
            mdls_tier=payload["clinical"].get("mdls_tier"),
            biomarker_flags=payload["clinical"].get("biomarker_flags"),
            mdls_derivatives=payload["clinical"].get("mdls_derivatives"),
            comorbidity_channels=payload["clinical"].get("comorbidity_channels"),
        )

        package = assign_package(decision_input)
        if package != expected["package"]:
            failures.append(f"{case_id}: package esperado {expected['package']} != {package}")

        recency_bucket = _recency_bucket(
            payload["temporal"]["recency_type"],
            payload["temporal"]["days_since_last_exam"],
        )
        if recency_bucket != expected["recency_bucket"]:
            failures.append(
                f"{case_id}: recency esperado {expected['recency_bucket']} != {recency_bucket}"
            )

        email_body = _placeholder_email(
            patient_name=payload["patient"]["patient_name"],
            recency_bucket=recency_bucket,
            package=package,
        )
        try:
            validate_email(email_body)
        except ComplianceError as exc:
            failures.append(f"{case_id}: compliance error {exc}")

        word_count = _word_count(email_body)
        if not 120 <= word_count <= 220:
            failures.append(f"{case_id}: longitud fuera de rango ({word_count} palabras)")

        block_count = _block_count(email_body)
        if block_count != 7:
            failures.append(f"{case_id}: bloques esperados 7 != {block_count}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(f"OK: {len(cases)} casos validados")
    return 0


def _recency_bucket(recency_type: str, days_since_last_exam: int) -> str:
    normalized = (recency_type or "").strip().upper()
    if normalized == "PRIMER_EXAMEN":
        return "PRIMER_EXAMEN"
    if days_since_last_exam > 365:
        return "HISTORICO_LARGO"
    if days_since_last_exam > 90:
        return "HISTORICO_MEDIO"
    return "HISTORICO_RECIENTE"


def _placeholder_email(*, patient_name: str, recency_bucket: str, package: str) -> str:
    recency_line = {
        "PRIMER_EXAMEN": "Queremos darle la bienvenida y compartirle esta invitación de forma cercana.",
        "HISTORICO_RECIENTE": "Este puede ser un buen momento para retomar un cuidado preventivo con calma.",
        "HISTORICO_MEDIO": "Retomar un acompañamiento estructurado puede ayudarle a sentirse más tranquilo.",
        "HISTORICO_LARGO": "Un chequeo periódico es una gran herramienta para mantener el equilibrio.",
    }[recency_bucket]

    package_line = {
        "STANDARD": "Incluye orientación general, hábitos saludables y apoyo básico para comenzar.",
        "SILVER": "Incluye seguimiento más activo, materiales guiados y coordinación de apoyo.",
        "GOLD": "Incluye acompañamiento integral, coordinación clínica y planificación continua.",
    }[package]

    paragraphs = [
        (
            f"Hola {patient_name}, esperamos que se encuentre muy bien y que su día transcurra con calma. "
            "Nos gustaría compartirle una invitación que puede ayudarle a fortalecer hábitos de bienestar."
        ),
        (
            f"{recency_line} Nuestro equipo busca entregar acompañamiento claro, cercano y comprensible, "
            "sin tecnicismos ni mensajes alarmistas."
        ),
        (
            "Queremos invitarle a conocer un programa preventivo pensado para acompañarle de forma clara, "
            "con orientación práctica para su cuidado diario."
        ),
        (
            f"{package_line} Además, puede incluir material educativo sencillo y un espacio para resolver dudas "
            "de manera ordenada."
        ),
        (
            "El objetivo es ofrecer información útil y apoyo continuo para que usted pueda tomar decisiones "
            "informadas y sentirse acompañado."
        ),
        (
            "Si le interesa, puede responder este correo para coordinar una conversación informativa o conocer "
            "los próximos pasos."
        ),
        (
            "Quedamos atentos para resolver cualquier duda con un enfoque cercano y respetuoso, "
            "siempre desde la prevención y el cuidado personal."
        ),
    ]
    return "\n\n".join(paragraphs)


def _word_count(text: str) -> int:
    return len([word for word in text.split() if word.strip()])


def _block_count(text: str) -> int:
    return len([block for block in text.split("\n\n") if block.strip()])


if __name__ == "__main__":
    raise SystemExit(main())

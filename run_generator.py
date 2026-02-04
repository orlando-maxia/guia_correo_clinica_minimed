"""Run the email generator with a JSON input payload and OpenAI LLM."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.decision_engine import DecisionInput, assign_package
from src.generator import generate_email
from src.static_content import assemble_full_email


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a full email from input JSON.")
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input JSON payload (see input_output_contract.md).",
    )
    parser.add_argument(
        "--api-key-file",
        help="Path to a file that contains OPENAI_API_KEY = <key>.",
    )
    parser.add_argument(
        "--model",
        default="gpt-4.1-mini",
        help="OpenAI model to use for generation.",
    )
    parser.add_argument(
        "--program-name",
        default="Programa Preventivo de Minimed",
        help="Program name shown to the patient (avoid prohibited terms).",
    )
    args = parser.parse_args()

    payload = _load_payload(Path(args.input))
    api_key = _resolve_api_key(args.api_key_file)

    client = OpenAI(api_key=api_key)

    def llm(prompt: str) -> str:
        response = client.responses.create(
            model=args.model,
            input=prompt,
        )
        return response.output_text

    decision_input = DecisionInput(
        mdls_calculable=payload["clinical"]["mdls_calculable"],
        mdls_tier=payload["clinical"].get("mdls_tier"),
        biomarker_flags=payload["clinical"].get("biomarker_flags"),
        mdls_derivatives=payload["clinical"].get("mdls_derivatives"),
        comorbidity_channels=payload["clinical"].get("comorbidity_channels"),
    )
    package = assign_package(decision_input)

    body = generate_email(
        patient_name=payload["patient"]["patient_name"],
        package=package,
        recency_type=payload["temporal"]["recency_type"],
        days_since_last_exam=payload["temporal"]["days_since_last_exam"],
        llm=llm,
        program_name=args.program_name,
    )

    final_email = assemble_full_email(body)
    print(final_email)
    return 0


def _load_payload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_api_key(api_key_file: str | None) -> str:
    if api_key_file:
        line = Path(api_key_file).read_text(encoding="utf-8").strip()
        return line.split("=", 1)[1].strip()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required (env or --api-key-file).")
    return api_key


if __name__ == "__main__":
    raise SystemExit(main())

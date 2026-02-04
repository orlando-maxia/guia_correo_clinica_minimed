import os
from openai import OpenAI
from src.generator import generate_email
from src.static_content import assemble_full_email
from src.decision_engine import DecisionInput, assign_package
import json
from pathlib import Path

payload = json.loads(Path("tests/sample_input.json").read_text(encoding="utf-8"))

patient_name = payload["patient"]["patient_name"]
recency_type = payload["temporal"]["recency_type"]
days_since_last_exam = payload["temporal"]["days_since_last_exam"]

decision_input = DecisionInput(
    mdls_calculable=payload["clinical"]["mdls_calculable"],
    mdls_tier=payload["clinical"].get("mdls_tier"),
    biomarker_flags=payload["clinical"].get("biomarker_flags"),
    mdls_derivatives=payload["clinical"].get("mdls_derivatives"),
    comorbidity_channels=payload["clinical"].get("comorbidity_channels"),
)

package = assign_package(decision_input)

def load_openai_key(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        line = f.read().strip()
    return line.split("=", 1)[1].strip()

# Ruta a tu archivo oaiak (ajústala)
api_key = load_openai_key(r"C:\Users\orlando.caballero\Downloads\oaiak")

client = OpenAI(api_key=api_key)

def llm(prompt: str) -> str:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return response.output_text

body = generate_email(
    patient_name=patient_name,
    package=package,
    recency_type=recency_type,
    days_since_last_exam=days_since_last_exam,
    llm=llm,
    program_name="Programa Preventivo de Minimed"
)

final_email = assemble_full_email(body)
print(final_email)



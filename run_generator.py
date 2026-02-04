import os
from openai import OpenAI
from src.generator import generate_email
from src.static_content import assemble_full_email

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
    patient_name="Ana",
    package="STANDARD",
    recency_type="HISTORICO",
    days_since_last_exam=40,
    llm=llm,
)

final_email = assemble_full_email(body)
print(final_email)

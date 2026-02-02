"""Static institutional content appended outside the LLM."""
from __future__ import annotations

from pathlib import Path


def assemble_full_email(
    email_body: str,
    *,
    include_disclaimer: bool = True,
    include_signature: bool = True,
) -> str:
    """Append fixed institutional content to the email body."""
    sections = [email_body.strip()]
    if include_disclaimer:
        sections.append(_load_disclaimer())
    if include_signature:
        sections.append(_load_signature())
    return "\n\n".join(section for section in sections if section)


def _load_disclaimer() -> str:
    return _read_text("static/disclaimer.txt")


def _load_signature() -> str:
    return _read_text("static/signature.txt")


def _read_text(relative_path: str) -> str:
    repo_root = Path(__file__).resolve().parents[1]
    return (repo_root / relative_path).read_text(encoding="utf-8").strip()

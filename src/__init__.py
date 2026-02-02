"""Core package for the email generator."""

from .compliance import ComplianceError, validate_email
from .generator import build_prompt, generate_email
from .static_content import assemble_full_email

__all__ = [
    "ComplianceError",
    "assemble_full_email",
    "build_prompt",
    "generate_email",
    "validate_email",
]
__all__ = ["ComplianceError", "build_prompt", "generate_email", "validate_email"]

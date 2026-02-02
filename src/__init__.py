"""Core package for the email generator."""

from .compliance import ComplianceError, validate_email
from .generator import build_prompt, generate_email

__all__ = ["ComplianceError", "build_prompt", "generate_email", "validate_email"]

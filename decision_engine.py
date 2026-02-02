"""Deterministic decision engine for package assignment.

This module intentionally avoids any ML/LLM usage. It only derives the
package label used later by the prompt/generator layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional


MDLS_TIER_TO_PACKAGE = {
    "BAJO": "STANDARD",
    "MEDIO": "SILVER",
    "ALTO": "GOLD",
}

BIOMARKER_RISK_TO_PACKAGE = {
    "BAJO": "STANDARD",
    "MEDIO": "SILVER",
    "ALTO": "GOLD",
}

GLUCOSE_MARKERS = {"GLU", "HBA1C"}
LIPID_MARKERS = {"TG", "VLDL", "HDL", "LDL", "NON_HDL"}
HEPATIC_MARKERS = {"ALT", "AST_ALT_RATIO"}


@dataclass(frozen=True)
class DecisionInput:
    """Inputs required to determine the package without AI."""

    mdls_calculable: bool
    mdls_tier: Optional[str] = None
    biomarker_flags: Optional[Mapping[str, str]] = None
    mdls_derivatives: Optional[Mapping[str, float]] = None
    comorbidity_channels: Optional[Mapping[str, float]] = None


class DecisionEngineError(ValueError):
    """Raised when decision inputs are inconsistent or incomplete."""


def assign_package(decision_input: DecisionInput) -> str:
    """Assign the membership package based on deterministic rules.

    Args:
        decision_input: Input object containing clinical segmentation signals.

    Returns:
        Package label: STANDARD, SILVER, or GOLD.
    """

    if decision_input.mdls_calculable:
        if not decision_input.mdls_tier:
            raise DecisionEngineError("mdls_tier is required when mdls_calculable is true")
        return _package_from_tier(decision_input.mdls_tier, MDLS_TIER_TO_PACKAGE)

    biomarker_risk_tier = derive_biomarker_risk_tier(
        decision_input.biomarker_flags,
        decision_input.mdls_derivatives,
        decision_input.comorbidity_channels,
    )
    return _package_from_tier(biomarker_risk_tier, BIOMARKER_RISK_TO_PACKAGE)


def derive_biomarker_risk_tier(
    biomarker_flags: Optional[Mapping[str, str]],
    mdls_derivatives: Optional[Mapping[str, float]],
    comorbidity_channels: Optional[Mapping[str, float]],
) -> str:
    """Derive a conservative biomarker risk tier from available flags.

    The rules follow the guidance in `guia_v1.md`:
    - Require at least two related biomarkers, or one biomarker + comorbidity
      channel, to elevate beyond BAJO.
    - Prefer ALTO when glucose + lipid, hepatic + metabolic, or renal +
      metabolic patterns are present.
    - Use MEDIO for consistent but less severe patterns, including a single
      clinically relevant biomarker or comorbidity channel when that is the
      only available signal.
    """

    flags = {k: (v or "").upper() for k, v in (biomarker_flags or {}).items()}
    derivatives = {k: v for k, v in (mdls_derivatives or {}).items()}
    comorbidities = {k: v for k, v in (comorbidity_channels or {}).items()}

    abnormal_markers = {marker for marker, status in flags.items() if status == "FUERA_RANGO"}
    glucose_abnormal = bool(abnormal_markers.intersection(GLUCOSE_MARKERS))
    lipid_abnormal = bool(abnormal_markers.intersection(LIPID_MARKERS))
    hepatic_abnormal = bool(abnormal_markers.intersection(HEPATIC_MARKERS))

    derivative_abnormal = any(value for value in derivatives.values())
    renal_abnormal = any(value for value in comorbidities.values())

    metabolic_support = lipid_abnormal or derivative_abnormal

    if (glucose_abnormal and metabolic_support) or (hepatic_abnormal and metabolic_support) or (
        renal_abnormal and (glucose_abnormal or metabolic_support)
    ):
        return "ALTO"

    lipid_markers = _count_abnormal(flags, LIPID_MARKERS)
    glucose_support = glucose_abnormal or derivative_abnormal

    if lipid_markers >= 2 or (glucose_abnormal and glucose_support):
        return "MEDIO"

    if renal_abnormal and (glucose_abnormal or lipid_abnormal):
        return "MEDIO"

    if len(abnormal_markers) == 1:
        sole_marker = next(iter(abnormal_markers))
        if sole_marker in {"GLU", "HBA1C", "TG", "VLDL"}:
            return "MEDIO"

    if renal_abnormal and not abnormal_markers:
        return "MEDIO"

    if glucose_abnormal or lipid_abnormal or hepatic_abnormal or renal_abnormal:
        return "BAJO"

    return "BAJO"


def _package_from_tier(tier: str, mapping: Mapping[str, str]) -> str:
    normalized = (tier or "").strip().upper()
    if normalized not in mapping:
        raise DecisionEngineError(f"Unknown tier: {tier}")
    return mapping[normalized]


def _count_abnormal(flags: Mapping[str, str], markers: set[str]) -> int:
    return sum(1 for marker in markers if flags.get(marker, "") == "FUERA_RANGO")

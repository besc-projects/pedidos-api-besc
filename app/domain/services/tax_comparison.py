"""Comparação declarado × referência fiscal (SUPRA), campo a campo.

Mesma convenção de `besc-commercial-report/src/reports/tax_divergence.py`
(`_TAX_FIELDS`/`_diverges`): NCM e Origem comparam como texto; ICMS, IPI e
ICMS ST comparam numericamente (evita falso positivo por "18" vs "18.0").
"""
from __future__ import annotations

from typing import Any

#: (nome exibido, campo no produto/referência, é percentual?)
TAX_FIELDS = (
    ("NCM", "ncm_code", False),
    ("Origem", "origin", False),
    ("ICMS", "icms", True),
    ("IPI", "ipi", True),
    ("ICMS ST", "icms_st", True),
)


def diverges(declared: Any, correct: Any, *, is_percentage: bool) -> bool:
    if declared is None and correct is None:
        return False
    if is_percentage:
        try:
            return round(float(declared or 0), 4) != round(float(correct or 0), 4)
        except (TypeError, ValueError):
            return declared != correct
    return str(declared or "").strip() != str(correct or "").strip()


def compare_fields(declared: dict[str, Any], correct: dict[str, Any]) -> list[dict]:
    """Uma linha por campo fiscal, com o valor declarado, o correto e se divergem."""
    rows = []
    for label, field_name, is_percentage in TAX_FIELDS:
        declared_value = declared.get(field_name)
        correct_value = correct.get(field_name)
        rows.append(
            {
                "name": label,
                "declared": _to_json(declared_value),
                "correct": _to_json(correct_value),
                "diverges": diverges(
                    declared_value, correct_value, is_percentage=is_percentage
                ),
            }
        )
    return rows


def _to_json(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "quantize"):  # Decimal
        return float(value)
    return value

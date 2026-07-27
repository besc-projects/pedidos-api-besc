from datetime import datetime
from typing import Optional

from app.domain.exceptions import ValidationException


class Invoice:
    """Domain entity for an issued invoice (nota fiscal).

    Framework-agnostic: guarantees the consistency of its own state only.
    Stage 1 fills `issue_code`; stage 2 (transmission) fills `transmission_code`.
    """

    def __init__(
        self,
        *,
        order_id: int,
        supra_id: int,
        issue_code: str,
        transmission_code: Optional[str] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self.id = id
        self.order_id = order_id
        self.supra_id = supra_id
        self.issue_code = issue_code
        self.transmission_code = transmission_code
        self.created_at = created_at
        self.updated_at = updated_at

        self._ensure_valid()

    def _ensure_valid(self) -> None:
        if not self.issue_code:
            raise ValidationException("issue_code is required.")

    def is_transmitted(self) -> bool:
        return bool(self.transmission_code)

    def set_transmission(self, transmission_code: str) -> None:
        self.transmission_code = transmission_code

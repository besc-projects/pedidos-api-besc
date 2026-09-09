from datetime import datetime
from typing import Optional

from app.domain.exceptions import ValidationException


class FiscalNotification:
    """Domain entity: registro de que um produto já foi avisado por falta de
    cadastro fiscal. Framework-agnostic — não sabe de FastAPI/SQLAlchemy/HTTP.
    """

    def __init__(
        self,
        *,
        part_number: str,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        if not part_number or not part_number.strip():
            raise ValidationException("part_number must not be empty.")

        self.id = id
        self.part_number = part_number.strip()
        self.created_at = created_at
        self.updated_at = updated_at

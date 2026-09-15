from datetime import datetime
from typing import Optional

from app.domain.exceptions import ValidationException


class Invoice:
    """Domain entity for an issued invoice (nota fiscal).

    Framework-agnostic: guarantees the consistency of its own state only.
    Stage 1 fills `id_emissao`/`data`; stage 2 (transmission) fills
    `id_transmissao`/`nfe`.
    """

    def __init__(
        self,
        *,
        order_id: int,
        id_emissao: int,
        data: datetime,
        id_transmissao: Optional[int] = None,
        nfe: Optional[str] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self.id = id
        self.order_id = order_id
        self.id_emissao = id_emissao
        self.data = data
        self.id_transmissao = id_transmissao
        self.nfe = nfe
        self.created_at = created_at
        self.updated_at = updated_at

        self._ensure_valid()

    def _ensure_valid(self) -> None:
        if not self.id_emissao:
            raise ValidationException("id_emissao is required.")
        if not self.data:
            raise ValidationException("data is required.")

    def is_transmitted(self) -> bool:
        return bool(self.id_transmissao)

    def set_transmission(
        self, id_transmissao: Optional[int], nfe: Optional[str] = None
    ) -> None:
        self.id_transmissao = id_transmissao
        self.nfe = nfe

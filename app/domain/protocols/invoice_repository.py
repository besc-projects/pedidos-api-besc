from typing import Optional, Protocol

from app.domain.entities.invoice import Invoice


class InvoiceRepositoryProtocol(Protocol):
    """Persistence contract for invoices (notas fiscais)."""

    async def get_by_id(self, invoice_id: int) -> Optional[Invoice]:
        ...

    async def get_by_order_id(self, order_id: int) -> Optional[Invoice]:
        ...

    async def list(
        self,
        order_id: Optional[int] = None,
        pending_transmission: Optional[bool] = None,
    ) -> list[Invoice]:
        ...

    async def create(self, invoice: Invoice) -> Invoice:
        ...

    async def update(self, invoice: Invoice) -> Invoice:
        ...

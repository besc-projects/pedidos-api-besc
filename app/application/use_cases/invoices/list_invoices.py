from app.domain.entities.invoice import Invoice
from app.domain.protocols.invoice_repository import InvoiceRepositoryProtocol
from app.schemas.invoices import InvoiceFilter


class ListInvoicesUseCase:
    """List invoices, optionally by order or by pending transmission."""

    def __init__(self, repository: InvoiceRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, filters: InvoiceFilter) -> list[Invoice]:
        return await self._repository.list(
            order_id=filters.order_id,
            pending_transmission=filters.pending_transmission,
        )

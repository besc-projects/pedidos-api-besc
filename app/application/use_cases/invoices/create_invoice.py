from app.domain.entities.invoice import Invoice
from app.domain.exceptions import ConflictException, NotFoundException
from app.domain.protocols.invoice_repository import InvoiceRepositoryProtocol
from app.schemas.invoices import InvoiceCreate


class CreateInvoiceUseCase:
    """Register an issued invoice; rejects a second one for the same order."""

    def __init__(self, repository: InvoiceRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, data: InvoiceCreate) -> Invoice:
        invoice = Invoice(
            order_id=data.order_id,
            supra_id=data.supra_id,
            issue_code=data.issue_code,
            transmission_code=data.transmission_code,
        )

        if not await self._repository.order_exists(invoice.order_id):
            raise NotFoundException(
                f"Order {invoice.order_id} not found. "
                "Use the internal order id, not vale_order_id."
            )

        already_exists = await self._repository.get_by_order_id(invoice.order_id)
        if already_exists is not None:
            raise ConflictException(
                "An invoice already exists for this order."
            )

        return await self._repository.create(invoice)

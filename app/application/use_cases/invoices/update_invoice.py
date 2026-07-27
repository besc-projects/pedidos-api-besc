from app.domain.entities.invoice import Invoice
from app.domain.exceptions import NotFoundException, ValidationException
from app.domain.protocols.invoice_repository import InvoiceRepositoryProtocol
from app.schemas.invoices import InvoiceUpdate


class UpdateInvoiceUseCase:
    """Update an invoice — usado na etapa 2 para gravar o transmissao_codigo."""

    def __init__(self, repository: InvoiceRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, invoice_id: int, data: InvoiceUpdate) -> Invoice:
        invoice = await self._repository.get_by_id(invoice_id)
        if invoice is None:
            raise NotFoundException("Invoice not found.")

        changes = data.model_dump(exclude_unset=True)
        if not changes:
            raise ValidationException("No fields to update.")

        if "transmission_code" in changes:
            invoice.set_transmission(changes["transmission_code"])

        return await self._repository.update(invoice)

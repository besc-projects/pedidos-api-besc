from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.invoices.create_invoice import CreateInvoiceUseCase
from app.application.use_cases.invoices.list_invoices import ListInvoicesUseCase
from app.application.use_cases.invoices.update_invoice import UpdateInvoiceUseCase
from app.database import get_db
from app.domain.protocols.invoice_repository import InvoiceRepositoryProtocol
from app.infrastructure.repositories.invoice_repository import (
    SqlAlchemyInvoiceRepository,
)


def get_invoice_repository(
    db: AsyncSession = Depends(get_db),
) -> InvoiceRepositoryProtocol:
    return SqlAlchemyInvoiceRepository(db)


def get_create_invoice_use_case(
    repository: InvoiceRepositoryProtocol = Depends(get_invoice_repository),
) -> CreateInvoiceUseCase:
    return CreateInvoiceUseCase(repository)


def get_list_invoices_use_case(
    repository: InvoiceRepositoryProtocol = Depends(get_invoice_repository),
) -> ListInvoicesUseCase:
    return ListInvoicesUseCase(repository)


def get_update_invoice_use_case(
    repository: InvoiceRepositoryProtocol = Depends(get_invoice_repository),
) -> UpdateInvoiceUseCase:
    return UpdateInvoiceUseCase(repository)

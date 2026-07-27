from app.domain.entities.price_table_entry import PriceTableEntry
from app.domain.exceptions import ConflictException, NotFoundException
from app.domain.protocols.price_table_repository import PriceTableRepositoryProtocol
from app.schemas.price_table import PriceTableCreate, PriceTableUpdate


class CreatePriceTableEntryUseCase:
    """Create a price-table entry, enforcing uniqueness of (pn, destination)."""

    def __init__(self, repository: PriceTableRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, data: PriceTableCreate) -> PriceTableEntry:
        entry = PriceTableEntry(
            pn=data.pn,
            long_description=data.long_description,
            description=data.description,
            destination=data.destination,
            unit_price=data.unit_price,
        )
        existing = await self._repository.get_by_pn_and_destination(
            entry.pn, entry.destination
        )
        if existing is not None:
            raise ConflictException(
                f"Product with PN '{entry.pn}' already exists "
                f"for destination '{entry.destination}'."
            )
        return await self._repository.create(entry)


class GetPriceTableEntryUseCase:
    """Retrieve a price-table entry by id."""

    def __init__(self, repository: PriceTableRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, entry_id: int) -> PriceTableEntry:
        entry = await self._repository.get_by_id(entry_id)
        if entry is None:
            raise NotFoundException(f"Price table entry with ID {entry_id} not found.")
        return entry


class GetPriceByPnUseCase:
    """Retrieve a price-table entry by PN and destination."""

    def __init__(self, repository: PriceTableRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, pn: str, state: str) -> PriceTableEntry:
        destination = PriceTableEntry.normalize_destination(state)
        entry = await self._repository.get_by_pn_and_destination(pn, destination)
        if entry is None:
            raise NotFoundException(
                f"Product with PN '{pn}' not found for destination '{destination}'."
            )
        return entry


class ListPriceTableEntriesUseCase:
    """List price-table entries with pagination."""

    def __init__(self, repository: PriceTableRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, skip: int, limit: int) -> list[PriceTableEntry]:
        return await self._repository.list(skip, limit)


class UpdatePriceTableEntryUseCase:
    """Apply a partial update to a price-table entry."""

    def __init__(self, repository: PriceTableRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, entry_id: int, data: PriceTableUpdate) -> PriceTableEntry:
        entry = await self._repository.get_by_id(entry_id)
        if entry is None:
            raise NotFoundException(f"Price table entry with ID {entry_id} not found.")

        changes = data.model_dump(exclude_unset=True)
        if "destination" in changes:
            changes["destination"] = PriceTableEntry.normalize_destination(
                changes["destination"]
            )
        return await self._repository.update(entry, changes)


class DeletePriceTableEntryUseCase:
    """Delete a price-table entry by id."""

    def __init__(self, repository: PriceTableRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, entry_id: int) -> None:
        deleted = await self._repository.delete(entry_id)
        if not deleted:
            raise NotFoundException(f"Price table entry with ID {entry_id} not found.")


class CheckPnExistsUseCase:
    """Check whether a PN already exists for a given destination."""

    def __init__(self, repository: PriceTableRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, pn: str, state: str) -> bool:
        destination = PriceTableEntry.normalize_destination(state)
        entry = await self._repository.get_by_pn_and_destination(pn, destination)
        return entry is not None

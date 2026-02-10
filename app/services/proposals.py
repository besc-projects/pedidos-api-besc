from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from fastapi import HTTPException, status

from app.models.proposals import Proposal as ProposalModel
from app.schemas.proposals import ProposalCreate, ProposalUpdate, Proposal


# 🟢 Create a new proposal
async def create_proposal(db: AsyncSession, proposal_in: ProposalCreate) -> Proposal:
    """
    Create a new proposal in the database.
    """
    # Check for duplicate proposal_numbe
    if proposal_in.proposal_number:
        result = await db.execute(
            select(ProposalModel).filter(
                ProposalModel.proposal_number == proposal_in.proposal_number
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Proposal number {proposal_in.proposal_number} already exists.",
            )

    db_proposal = ProposalModel(**proposal_in.model_dump())
    db.add(db_proposal)
    await db.commit()
    await db.refresh(db_proposal)

    return Proposal.model_validate(db_proposal, from_attributes=True)


# 🔵 Get a proposal by ID
async def get_proposal(db: AsyncSession, proposal_id: int) -> Proposal:
    """
    Retrieve a proposal by its ID.
    """
    result = await db.execute(
        select(ProposalModel).filter(ProposalModel.id == proposal_id)
    )
    proposal = result.scalar_one_or_none()

    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found.",
        )

    return Proposal.model_validate(proposal, from_attributes=True)


# 🟣 Update a proposal
async def update_proposal(
    db: AsyncSession, proposal_id: int, proposal_in: ProposalUpdate
) -> Proposal:
    """
    Update a proposal by ID.
    """
    result = await db.execute(
        select(ProposalModel).filter(ProposalModel.id == proposal_id)
    )
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found.",
        )

    for key, value in proposal_in.model_dump(exclude_unset=True).items():
        setattr(proposal, key, value)

    db.add(proposal)
    await db.commit()
    await db.refresh(proposal)

    return Proposal.model_validate(proposal, from_attributes=True)


# 🔴 Delete a proposal
async def delete_proposal(db: AsyncSession, proposal_id: int) -> bool:
    """
    Delete a proposal by its ID.
    """
    result = await db.execute(
        select(ProposalModel).filter(ProposalModel.id == proposal_id)
    )
    proposal = result.scalar_one_or_none()
    if not proposal:
        return False

    await db.execute(delete(ProposalModel).where(ProposalModel.id == proposal_id))
    await db.commit()
    return True

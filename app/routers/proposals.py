from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.proposals import (
    create_proposal,
    get_proposal,
    delete_proposal,
    proposal_exists,
    update_proposal,
)
from app.schemas.proposals import Proposal, ProposalCreate, ProposalUpdate

router = APIRouter(prefix="/api/proposals", tags=["Proposals"])


# 🟢 Create proposal
@router.post("/", response_model=Proposal, status_code=status.HTTP_201_CREATED)
async def create_proposal_route(
    proposal: ProposalCreate, db: AsyncSession = Depends(get_db)
):
    """
    Create a new proposal.
    """
    return await create_proposal(db, proposal)


# 🔵 Get proposal by ID
@router.get("/{id}", response_model=Proposal)
async def get_proposal_route(id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a proposal by its ID..
    """
    return await get_proposal(db, id)

@router.get("/exists/{proposal_number}", response_model=bool)
async def check_proposal_exists_route(proposal_number: str, db: AsyncSession = Depends(get_db)):
    """Check if a proposal with the given proposal_number exists.
    """   
    return await proposal_exists(db, proposal_number)


# 🟣 Update proposal
@router.put("/{id}", response_model=Proposal)
async def update_proposal_route(
    id: int, proposal: ProposalUpdate, db: AsyncSession = Depends(get_db)
):
    """
    Update an existing proposal.
    """
    return await update_proposal(db, id, proposal)


# 🔴 Delete proposal
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_proposal_route(id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a proposal by its ID.
    """
    deleted = await delete_proposal(db, id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found."
        )
    return None

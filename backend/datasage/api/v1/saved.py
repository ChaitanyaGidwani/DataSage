"""Saved properties endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException

from datasage.api.deps import get_current_user
from datasage.core.database import get_session
from datasage.models.user import User
from datasage.repositories.interaction_repo import SavedPropertyRepository

router = APIRouter()


@router.get("")
async def list_saved(
    limit: int = 50,
    offset: int = 0,
    user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    """List user's saved properties."""
    repo = SavedPropertyRepository(session)
    saved = await repo.get_by_user(user.id, limit=limit, offset=offset)
    return {
        "data": [
            {
                "id": str(s.id),
                "property_id": str(s.property_id),
                "created_at": s.created_at.isoformat(),
            }
            for s in saved
        ]
    }


@router.post("", status_code=201)
async def save_property(
    body: dict,
    user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    """Save a property to the user's list."""
    property_id = body.get("property_id")
    if not property_id:
        raise HTTPException(status_code=422, detail="property_id is required")

    try:
        parsed_id = uuid.UUID(property_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid property_id UUID format")

    repo = SavedPropertyRepository(session)
    saved = await repo.save(user.id, parsed_id)
    return {"id": str(saved.id), "property_id": str(saved.property_id)}


@router.delete("/{property_id}", status_code=204)
async def unsave_property(
    property_id: str,
    user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    """Remove a property from the user's saved list."""
    try:
        parsed_id = uuid.UUID(property_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Saved property not found")

    repo = SavedPropertyRepository(session)
    removed = await repo.unsave(user.id, parsed_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Saved property not found")

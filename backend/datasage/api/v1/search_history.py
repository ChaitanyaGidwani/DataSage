"""Search history endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from datasage.api.deps import get_current_user
from datasage.core.database import get_session
from datasage.models.user import User
from datasage.repositories.interaction_repo import SearchHistoryRepository

router = APIRouter()


@router.get("")
async def list_search_history(
    limit: int = 20,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Get user's recent search history."""
    repo = SearchHistoryRepository(session)
    history = await repo.get_by_user(user.id, limit=limit)
    return {
        "data": [
            {
                "id": str(h.id),
                "query_params": h.query_params,
                "result_count": h.result_count,
                "created_at": h.created_at.isoformat(),
            }
            for h in history
        ]
    }


@router.delete("", status_code=204, response_class=Response)
async def clear_search_history(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Response:
    """Clear all search history for the current user."""
    repo = SearchHistoryRepository(session)
    await repo.clear_for_user(user.id)
    return Response(status_code=204)

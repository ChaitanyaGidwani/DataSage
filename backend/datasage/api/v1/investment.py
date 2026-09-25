"""Investment analysis API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from datasage.core.database import get_session
from datasage.schemas.investment import InvestmentAnalysisResponse
from datasage.services.investment_service import InvestmentService

router = APIRouter()


@router.get("/{property_id}", response_model=InvestmentAnalysisResponse)
async def get_property_investment(
    property_id: str,
    session: AsyncSession = Depends(get_session),
) -> InvestmentAnalysisResponse:
    """Get investment rating, rental yield, CAGR, and 5-year capital appreciation forecast."""
    service = InvestmentService(session)
    return await service.analyze_property(property_id)

"""Aggregate all v1 API routers."""

from __future__ import annotations

from fastapi import APIRouter

from datasage.api.v1.admin import router as admin_router
from datasage.api.v1.auth import router as auth_router
from datasage.api.v1.comparison import router as comparison_router
from datasage.api.v1.investment import router as investment_router
from datasage.api.v1.localities import router as localities_router
from datasage.api.v1.location import router as location_router
from datasage.api.v1.preferences import router as preferences_router
from datasage.api.v1.properties import router as properties_router
from datasage.api.v1.recommendations import router as recommendations_router
from datasage.api.v1.saved import router as saved_router
from datasage.api.v1.search_history import router as history_router
from datasage.api.v1.valuations import router as valuations_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(properties_router, prefix="/properties", tags=["Properties"])
api_v1_router.include_router(localities_router, prefix="/localities", tags=["Localities"])
api_v1_router.include_router(saved_router, prefix="/saved-properties", tags=["Saved Properties"])
api_v1_router.include_router(history_router, prefix="/search-history", tags=["Search History"])
api_v1_router.include_router(preferences_router, prefix="/preferences", tags=["Preferences"])
api_v1_router.include_router(valuations_router, prefix="/valuations", tags=["Valuations"])
api_v1_router.include_router(comparison_router, prefix="/comparison", tags=["Comparison"])
api_v1_router.include_router(location_router, prefix="/location", tags=["Location Intelligence"])
api_v1_router.include_router(investment_router, prefix="/investment", tags=["Investment Analysis"])
api_v1_router.include_router(recommendations_router, prefix="/recommendations", tags=["Recommendations"])
api_v1_router.include_router(admin_router, prefix="/admin", tags=["Admin"])



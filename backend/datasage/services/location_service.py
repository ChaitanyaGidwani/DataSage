"""Geospatial & Location Intelligence Service.

Computes composite location scores, category subscores, and nearby POIs
for properties in Delhi-NCR, following docs/14-geospatial-system.md.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from datasage.models.property import Property
from datasage.models.reference import Locality
from datasage.schemas.location import (
    LocationScoreResponse,
    LocationSubScores,
    POIItem,
)

logger = logging.getLogger(__name__)

# Locality-specific infrastructure profiles for Delhi-NCR
LOCALITY_GEO_PROFILES: dict[str, dict[str, Any]] = {
    # Central / South Delhi
    "Vasant Kunj": {"metro_dist": 1.2, "metro_name": "Chattarpur Metro", "hospital_dist": 0.8, "school_dist": 0.6, "park_dist": 0.3, "mall_dist": 1.0},
    "Hauz Khas": {"metro_dist": 0.4, "metro_name": "Hauz Khas Metro (Interchange)", "hospital_dist": 1.5, "school_dist": 0.5, "park_dist": 0.2, "mall_dist": 1.2},
    "Greater Kailash I": {"metro_dist": 0.6, "metro_name": "Greater Kailash Metro", "hospital_dist": 1.1, "school_dist": 0.7, "park_dist": 0.4, "mall_dist": 0.5},
    "Greater Kailash II": {"metro_dist": 0.8, "metro_name": "Enclave Metro", "hospital_dist": 1.3, "school_dist": 0.8, "park_dist": 0.3, "mall_dist": 0.4},
    "Saket": {"metro_dist": 0.5, "metro_name": "Saket Metro", "hospital_dist": 0.4, "school_dist": 0.7, "park_dist": 0.6, "mall_dist": 0.3},
    "Dwarka Sector 10": {"metro_dist": 0.3, "metro_name": "Dwarka Sector 10 Metro", "hospital_dist": 1.2, "school_dist": 0.4, "park_dist": 0.5, "mall_dist": 0.8},
    "Dwarka Sector 21": {"metro_dist": 0.2, "metro_name": "Dwarka Sector 21 (Airport Express)", "hospital_dist": 2.0, "school_dist": 0.9, "park_dist": 0.6, "mall_dist": 1.5},
    # Gurgaon
    "DLF Phase 1": {"metro_dist": 0.5, "metro_name": "Sikanderpur Metro", "hospital_dist": 1.2, "school_dist": 0.8, "park_dist": 0.4, "mall_dist": 0.9},
    "DLF Phase 2": {"metro_dist": 0.3, "metro_name": "Vodafone Belvedere Towers Metro", "hospital_dist": 1.0, "school_dist": 0.7, "park_dist": 0.5, "mall_dist": 0.4},
    "DLF Phase 5": {"metro_dist": 0.6, "metro_name": "Sector 53-54 Metro", "hospital_dist": 0.7, "school_dist": 0.5, "park_dist": 0.3, "mall_dist": 0.6},
    "Golf Course Road": {"metro_dist": 0.4, "metro_name": "Sector 54 Chowk Metro", "hospital_dist": 1.2, "school_dist": 0.6, "park_dist": 0.4, "mall_dist": 0.8},
    "Golf Course Extension": {"metro_dist": 2.2, "metro_name": "Sector 55-56 Metro", "hospital_dist": 1.8, "school_dist": 0.8, "park_dist": 0.6, "mall_dist": 1.4},
    "Sector 57": {"metro_dist": 1.8, "metro_name": "Sector 56 Metro", "hospital_dist": 2.1, "school_dist": 0.9, "park_dist": 0.5, "mall_dist": 1.2},
    "Sector 82": {"metro_dist": 4.5, "metro_name": "Huda City Centre (Feeder)", "hospital_dist": 3.0, "school_dist": 1.2, "park_dist": 0.8, "mall_dist": 2.0},
    # Noida
    "Sector 15": {"metro_dist": 0.3, "metro_name": "Noida Sector 15 Metro", "hospital_dist": 1.0, "school_dist": 0.6, "park_dist": 0.4, "mall_dist": 0.7},
    "Sector 18": {"metro_dist": 0.2, "metro_name": "Noida Sector 18 Metro", "hospital_dist": 0.9, "school_dist": 1.1, "park_dist": 0.5, "mall_dist": 0.1},
    "Sector 62": {"metro_dist": 0.4, "metro_name": "Noida Electronic City Metro", "hospital_dist": 0.8, "school_dist": 0.5, "park_dist": 0.4, "mall_dist": 1.2},
    "Sector 75": {"metro_dist": 0.6, "metro_name": "Sector 76 Metro", "hospital_dist": 1.5, "school_dist": 0.8, "park_dist": 0.5, "mall_dist": 0.8},
    "Sector 137": {"metro_dist": 0.4, "metro_name": "Sector 137 Metro (Aqua Line)", "hospital_dist": 0.6, "school_dist": 0.9, "park_dist": 0.3, "mall_dist": 1.5},
    "Sector 150": {"metro_dist": 2.8, "metro_name": "Sector 148 Metro", "hospital_dist": 3.5, "school_dist": 1.4, "park_dist": 0.2, "mall_dist": 3.0},
    # Ghaziabad / Faridabad
    "Indirapuram": {"metro_dist": 2.1, "metro_name": "Vaishali Metro", "hospital_dist": 1.1, "school_dist": 0.5, "park_dist": 0.4, "mall_dist": 0.6},
    "Vaishali": {"metro_dist": 0.5, "metro_name": "Vaishali Metro", "hospital_dist": 0.8, "school_dist": 0.6, "park_dist": 0.4, "mall_dist": 0.5},
    "Vasundhara": {"metro_dist": 1.8, "metro_name": "Vaishali Metro", "hospital_dist": 1.2, "school_dist": 0.7, "park_dist": 0.5, "mall_dist": 0.9},
    "Sector 14 Faridabad": {"metro_dist": 1.4, "metro_name": "Neelam Chowk Ajronda Metro", "hospital_dist": 1.0, "school_dist": 0.6, "park_dist": 0.5, "mall_dist": 1.1},
    "Sector 15 Faridabad": {"metro_dist": 1.1, "metro_name": "Bata Chowk Metro", "hospital_dist": 1.2, "school_dist": 0.5, "park_dist": 0.4, "mall_dist": 0.9},
}

DEFAULT_GEO_PROFILE = {
    "metro_dist": 1.5,
    "metro_name": "Nearby Metro Station",
    "hospital_dist": 1.8,
    "school_dist": 1.0,
    "park_dist": 0.6,
    "mall_dist": 1.5,
}


def _distance_to_subscore(dist_km: float, max_walk_km: float = 1.0, max_good_km: float = 3.0) -> int:
    """Map distance in kilometers to a 0-100 score."""
    if dist_km <= max_walk_km:
        # 85 to 100
        return int(100 - (dist_km / max_walk_km) * 15)
    elif dist_km <= max_good_km:
        # 60 to 85
        return int(85 - ((dist_km - max_walk_km) / (max_good_km - max_walk_km)) * 25)
    else:
        # < 60 decay
        decay = (dist_km - max_good_km) * 8
        return max(20, int(60 - decay))


class LocationService:
    """Service for computing location intelligence and POI metrics."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_property_location_score(self, property_id: str) -> LocationScoreResponse:
        """Calculate or retrieve detailed location metrics for a property."""
        result = await self.session.execute(
            select(Property).where(Property.id == uuid.UUID(property_id))
        )
        prop = result.scalar_one_or_none()
        if not prop:
            from datasage.core.exceptions import NotFoundError
            raise NotFoundError("Property", property_id)

        # Get locality name
        locality_name = "Delhi-NCR"
        if prop.locality_id:
            loc_res = await self.session.execute(
                select(Locality).where(Locality.id == prop.locality_id)
            )
            loc = loc_res.scalar_one_or_none()
            if loc:
                locality_name = loc.name

        # Match profile or fallback
        profile = LOCALITY_GEO_PROFILES.get(locality_name, DEFAULT_GEO_PROFILE)
        metro_d = profile["metro_dist"]
        hosp_d = profile["hospital_dist"]
        school_d = profile["school_dist"]
        park_d = profile["park_dist"]
        mall_d = profile["mall_dist"]

        # Calculate sub-scores (0 to 100)
        # Transit: 30% weight
        transit_score = _distance_to_subscore(metro_d, max_walk_km=0.8, max_good_km=2.5)
        # Schools: 20% weight
        schools_score = _distance_to_subscore(school_d, max_walk_km=0.7, max_good_km=2.0)
        # Healthcare: 15% weight
        health_score = _distance_to_subscore(hosp_d, max_walk_km=1.0, max_good_km=3.0)
        # Shopping: 15% weight
        shop_score = _distance_to_subscore(mall_d, max_walk_km=0.8, max_good_km=2.5)
        # Parks: 10% weight
        parks_score = _distance_to_subscore(park_d, max_walk_km=0.5, max_good_km=1.5)
        # Dining: 10% weight
        dining_score = min(100, int((shop_score * 0.6) + (transit_score * 0.4)))

        # Composite score
        composite = int(
            transit_score * 0.30
            + schools_score * 0.20
            + health_score * 0.15
            + shop_score * 0.15
            + parks_score * 0.10
            + dining_score * 0.10
        )
        composite = max(1, min(99, composite))

        # Rating label
        if composite >= 85:
            label = "Excellent"
        elif composite >= 75:
            label = "Very Good"
        elif composite >= 65:
            label = "Good"
        elif composite >= 50:
            label = "Moderate"
        else:
            label = "Developing Connectivity"

        # Build nearest POIs
        metro_poi = POIItem(
            name=profile.get("metro_name", f"{locality_name} Metro Station"),
            category="metro",
            distance_meters=int(metro_d * 1000),
            distance_km=round(metro_d, 2),
            travel_time_minutes_walk=int(metro_d * 13),
            travel_time_minutes_drive=max(2, int(metro_d * 3)),
        )

        hosp_poi = POIItem(
            name=f"Max Super Speciality / Fortis Hospital ({locality_name})",
            category="hospital",
            distance_meters=int(hosp_d * 1000),
            distance_km=round(hosp_d, 2),
            travel_time_minutes_walk=int(hosp_d * 13),
            travel_time_minutes_drive=max(3, int(hosp_d * 3.5)),
        )

        school_poi = POIItem(
            name=f"Delhi Public School / Ryan International ({locality_name})",
            category="school",
            distance_meters=int(school_d * 1000),
            distance_km=round(school_d, 2),
            travel_time_minutes_walk=int(school_d * 13),
            travel_time_minutes_drive=max(2, int(school_d * 3)),
        )

        park_poi = POIItem(
            name=f"{locality_name} Central Park & Green Belt",
            category="park",
            distance_meters=int(park_d * 1000),
            distance_km=round(park_d, 2),
            travel_time_minutes_walk=int(park_d * 13),
            travel_time_minutes_drive=max(1, int(park_d * 2.5)),
        )

        mall_poi = POIItem(
            name=f"{locality_name} Galleria & High-Street Retail",
            category="shopping",
            distance_meters=int(mall_d * 1000),
            distance_km=round(mall_d, 2),
            travel_time_minutes_walk=int(mall_d * 13),
            travel_time_minutes_drive=max(2, int(mall_d * 3)),
        )

        nearby_list = [metro_poi, hosp_poi, school_poi, park_poi, mall_poi]

        summary_text = (
            f"{locality_name} scores {composite}/100 for location intelligence. "
            f"Nearest transit is {metro_poi.name} ({metro_d} km), with {school_poi.name} "
            f"within {school_d} km and prominent healthcare access at {hosp_d} km."
        )

        return LocationScoreResponse(
            property_id=prop.id,
            composite_score=composite,
            rating_label=label,
            sub_scores=LocationSubScores(
                transit=transit_score,
                schools=schools_score,
                healthcare=health_score,
                shopping=shop_score,
                parks=parks_score,
                dining=dining_score,
            ),
            nearest_metro=metro_poi,
            nearest_hospital=hosp_poi,
            nearest_school=school_poi,
            nearby_pois=nearby_list,
            location_summary=summary_text,
        )

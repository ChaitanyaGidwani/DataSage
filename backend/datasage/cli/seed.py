"""Seed data CLI — populate the database with reference data and synthetic properties.

Usage:
    python -m datasage.cli.seed --demo
    python -m datasage.cli.seed --demo --count 500
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import logging
import random
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from datasage.core.database import async_session_factory, engine
from datasage.core.security import hash_password
from datasage.models.base import Base
from datasage.models.property import Property
from datasage.models.reference import City, Locality
from datasage.models.user import User
from datasage.models.valuation import ModelVersion

logger = logging.getLogger(__name__)

# ── Reference data ─────────────────────────────────────────────────────────

CITIES = [
    {"id": 1, "name": "Noida", "state": "Uttar Pradesh"},
    {"id": 2, "name": "Gurgaon", "state": "Haryana"},
    {"id": 3, "name": "New Delhi", "state": "Delhi"},
    {"id": 4, "name": "Ghaziabad", "state": "Uttar Pradesh"},
    {"id": 5, "name": "Greater Noida", "state": "Uttar Pradesh"},
    {"id": 6, "name": "Faridabad", "state": "Haryana"},
]

PROPERTY_TYPES = ["apartment", "builder_floor", "house", "plot"]
FURNISHING_OPTIONS = ["unfurnished", "semi_furnished", "fully_furnished"]
FACING_OPTIONS = ["north", "south", "east", "west", "north_east", "north_west", "south_east", "south_west"]

SAMPLE_DESCRIPTIONS = [
    "Spacious {bhk} BHK {prop_type} in {locality} with modern amenities and great connectivity.",
    "Well-maintained {bhk} BHK {prop_type} near metro station in {locality}. Ready to move.",
    "Premium {bhk} BHK {prop_type} with club house, swimming pool, and 24/7 security in {locality}.",
    "Affordable {bhk} BHK {prop_type} in a gated society in {locality}. Power backup included.",
    "Luxury {bhk} BHK {prop_type} with panoramic views in {locality}. Vastu compliant.",
    "Newly constructed {bhk} BHK {prop_type} in {locality} with modular kitchen and covered parking.",
]


async def create_tables() -> None:
    """Create all tables if they don't exist (dev convenience)."""
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ensured.")


async def seed_cities_and_localities(session: AsyncSession) -> list[Locality]:
    """Insert cities and localities from CSV."""
    # Check if already seeded
    existing = await session.execute(text("SELECT COUNT(*) FROM city"))
    count = existing.scalar()
    if count is not None and count > 0:
        logger.info("Cities already seeded — skipping.")
        locs = await session.execute(select(Locality))
        return list(locs.scalars().all())

    # Insert cities
    for city_data in CITIES:
        city = City(**city_data)
        session.add(city)
    await session.flush()
    logger.info("Seeded %d cities.", len(CITIES))

    # Insert localities from CSV
    csv_path = Path(__file__).resolve().parents[3] / "data" / "seed" / "localities.csv"
    if not csv_path.exists():
        logger.error("Localities CSV not found at %s", csv_path)
        return []

    localities = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            loc = Locality(
                id=int(row["id"]),
                city_id=int(row["city_id"]),
                name=row["name"],
                slug=row["slug"],
                centroid_lat=float(row["centroid_lat"]),
                centroid_lng=float(row["centroid_lng"]),
                avg_price_per_sqft=float(row["avg_price_per_sqft"]) if row["avg_price_per_sqft"] else None,
                price_trend_1y_pct=float(row["price_trend_1y_pct"]) if row["price_trend_1y_pct"] else None,
                price_trend_3y_pct=float(row["price_trend_3y_pct"]) if row["price_trend_3y_pct"] else None,
            )
            session.add(loc)
            localities.append(loc)

    # Seed baseline heuristic model version for predictions
    heuristic_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    existing_mv = await session.execute(
        select(ModelVersion).where(ModelVersion.id == heuristic_id)
    )
    if existing_mv.scalar_one_or_none() is None:
        mv = ModelVersion(
            id=heuristic_id,
            version_label="v0.1-heuristic",
            algorithm="heuristic",
            is_active=True,
            trained_at=datetime.now(UTC),
        )
        session.add(mv)

    await session.flush()
    logger.info("Seeded %d localities and baseline model version.", len(localities))
    return localities


def _generate_property(locality: Locality, index: int) -> Property:
    """Generate a single synthetic property for a locality."""
    prop_type = random.choice(PROPERTY_TYPES)
    bhk = random.choices([1, 2, 3, 4, 5], weights=[10, 30, 40, 15, 5])[0]
    area_ranges = {1: (400, 700), 2: (700, 1200), 3: (1000, 1800), 4: (1500, 2500), 5: (2000, 4000)}
    min_area, max_area = area_ranges.get(bhk, (800, 1500))
    area = round(random.uniform(min_area, max_area), 0)

    base_price = (locality.avg_price_per_sqft or 6000) * area
    # Add ±30% variation
    price_variation = random.uniform(0.7, 1.3)
    price = int(base_price * price_variation)

    total_floors = random.randint(4, 25)
    floor_number = random.randint(1, total_floors) if prop_type != "plot" else None

    construction_year = random.randint(2010, 2026) if prop_type != "plot" else None

    title = f"{bhk} BHK {prop_type.replace('_', ' ').title()} in {locality.name}"
    description = random.choice(SAMPLE_DESCRIPTIONS).format(
        bhk=bhk,
        prop_type=prop_type.replace("_", " ").title(),
        locality=locality.name,
    )

    listed_at = datetime.now(UTC) - timedelta(days=random.randint(1, 180))

    # Derive lat/lng from locality centroid with slight random jitter (±0.01°, ~1km)
    lat = locality.centroid_lat + random.uniform(-0.01, 0.01) if locality.centroid_lat else None
    lng = locality.centroid_lng + random.uniform(-0.01, 0.01) if locality.centroid_lng else None

    return Property(
        city_id=locality.city_id,
        locality_id=locality.id,
        title=title,
        property_type=prop_type,
        bhk=bhk,
        area_sqft=area,
        listing_price=price,
        floor_number=floor_number,
        total_floors=total_floors if prop_type != "plot" else None,
        facing=random.choice(FACING_OPTIONS),
        construction_year=construction_year,
        furnishing=random.choice(FURNISHING_OPTIONS) if prop_type != "plot" else None,
        parking_count=random.randint(0, 2),
        balcony_count=random.randint(0, 3),
        bathroom_count=bhk + random.randint(0, 1),
        description=description,
        data_source="seed",
        listed_at=listed_at,
        latitude=lat,
        longitude=lng,
    )


async def seed_properties(session: AsyncSession, localities: list[Locality], count: int) -> None:
    """Generate and insert synthetic properties."""
    existing = await session.execute(text("SELECT COUNT(*) FROM property"))
    current_count = existing.scalar() or 0
    if current_count > 0:
        logger.info("Properties already seeded (%d found) — skipping.", current_count)
        return

    properties = []
    for i in range(count):
        locality = random.choice(localities)
        prop = _generate_property(locality, i)
        properties.append(prop)

    session.add_all(properties)
    await session.flush()
    logger.info("Seeded %d synthetic properties.", count)


async def run_seed(count: int = 1000) -> None:
    """Run the full seeding pipeline."""
    await create_tables()

    async with async_session_factory() as session:
        try:
            localities = await seed_cities_and_localities(session)
            if localities:
                await seed_properties(session, localities, count)

            # Seed heuristic model version
            sentinel_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
            existing_model = await session.execute(
                select(ModelVersion).where(ModelVersion.id == sentinel_id)
            )
            if not existing_model.scalar_one_or_none():
                mv = ModelVersion(
                    id=sentinel_id,
                    version_label="heuristic-v1",
                    algorithm="heuristic",
                    is_active=True,
                )
                session.add(mv)
                logger.info("Seeded heuristic model version.")

            # Seed demo user
            existing_user = await session.execute(
                select(User).where(User.email == "demo@datasage.ai")
            )
            if not existing_user.scalar_one_or_none():
                pw_hash = await asyncio.to_thread(hash_password, "DataSage@2026")
                demo = User(
                    name="Demo User",
                    email="demo@datasage.ai",
                    password_hash=pw_hash,
                    role="buyer",
                    is_active=True,
                    email_verified=True,
                )
                session.add(demo)
                logger.info("Seeded demo user (demo@datasage.ai / DataSage@2026).")

            # Seed admin user
            existing_admin = await session.execute(
                select(User).where(User.email == "admin@datasage.ai")
            )
            if not existing_admin.scalar_one_or_none():
                admin_pw_hash = await asyncio.to_thread(hash_password, "DataSage@2026")
                admin_user = User(
                    name="Admin User",
                    email="admin@datasage.ai",
                    password_hash=admin_pw_hash,
                    role="admin",
                    is_active=True,
                    email_verified=True,
                )
                session.add(admin_user)
                logger.info("Seeded admin user (admin@datasage.ai / DataSage@2026).")

            await session.commit()
            logger.info("Seeding complete.")
        except Exception:
            await session.rollback()
            logger.exception("Seeding failed.")
            raise


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="DataSage seed data loader")
    parser.add_argument("--demo", action="store_true", help="Seed demo data")
    parser.add_argument("--count", type=int, default=1000, help="Number of properties to generate")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

    if args.demo:
        asyncio.run(run_seed(count=args.count))
    else:
        print("Use --demo to seed demo data. Run with --help for more options.")
        sys.exit(1)


if __name__ == "__main__":
    main()

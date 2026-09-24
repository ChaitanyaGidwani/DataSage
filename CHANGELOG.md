# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete project documentation system (35+ documents)
- Project overview, product requirements, user personas, user flows
- System architecture, frontend/backend architecture, database design
- API specification, authentication/authorization design
- ML system design, feature engineering, geospatial system
- Recommendation engine, explainable AI documentation
- Data ingestion pipeline, data quality framework
- Security, privacy, error handling, observability specifications
- Testing strategy, deployment, environment configuration
- Project structure, development roadmap, MVP scope definition
- Risk register, acceptance criteria, AI agent rules, contributing guide
- Docker Compose configuration for local development
- Environment variable template (.env.example)

### Fixed
- **Frontend Linter & Type Warnings (13 Issues Resolved)**:
  - Replaced plain `<a>` tags with Next.js `<Link>` components in [`dashboard/page.tsx`](file:///c:/Users/siddi/DataSage/frontend/src/app/dashboard/page.tsx).
  - Cleaned up unused `formatINR` and connected `loading` skeleton states in [`dashboard/page.tsx`](file:///c:/Users/siddi/DataSage/frontend/src/app/dashboard/page.tsx).
  - Replaced loose `any` type with `ValuationData` interface in [`properties/[id]/page.tsx`](file:///c:/Users/siddi/DataSage/frontend/src/app/properties/[id]/page.tsx).
  - Decoupled synchronous `setLoading(true)` from mount effect in [`properties/page.tsx`](file:///c:/Users/siddi/DataSage/frontend/src/app/properties/page.tsx).
  - Utilized `imageUrl` prop for background-image card presentation in [`PropertyCard.tsx`](file:///c:/Users/siddi/DataSage/frontend/src/components/property/PropertyCard.tsx).
  - Wrapped synchronous `setIsLoading(false)` with `queueMicrotask` in [`AuthContext.tsx`](file:///c:/Users/siddi/DataSage/frontend/src/contexts/AuthContext.tsx).
  - Handled 401 redirect ESLint rule in non-React API client in [`api.ts`](file:///c:/Users/siddi/DataSage/frontend/src/lib/api.ts).
- Added comprehensive Backend Test Suite (`backend/tests/`) with 69 tests (32 unit tests and 37 integration/API tests) spanning Security, Valuation, Location Intelligence, Investment ROI, Property Comparison, Recommendations, Localities, Search History, Redis, and API endpoints.
- Resolved bcrypt >= 4.1.0 and passlib compatibility issue in [`security.py`](file:///c:/Users/siddi/DataSage/backend/datasage/core/security.py) by monkeypatching `__about__.__version__` to avoid trapped `AttributeError`.
- Made [`main.py`](file:///c:/Users/siddi/DataSage/backend/datasage/main.py) startup resilient against database connection failures during offline testing/dev.
- Fixed `city_id` query parameter type from `uuid.UUID` to `int` in [`recommendations.py`](file:///c:/Users/siddi/DataSage/backend/datasage/api/v1/recommendations.py) and [`recommendation_service.py`](file:///c:/Users/siddi/DataSage/backend/datasage/services/recommendation_service.py) to match the relational database schema.
- Added nested API sub-routes per `docs/10-api-specification.md` in [`properties.py`](file:///c:/Users/siddi/DataSage/backend/datasage/api/v1/properties.py): `/properties/{id}/valuation`, `/properties/{id}/location`, `/properties/{id}/investment`, and `/properties/{id}/similar`.
- Added `get_similar` comparable properties retrieval in [`PropertyService`](file:///c:/Users/siddi/DataSage/backend/datasage/services/property_service.py).
- Added safe UUID parsing across [`properties.py`](file:///c:/Users/siddi/DataSage/backend/datasage/api/v1/properties.py), [`comparison.py`](file:///c:/Users/siddi/DataSage/backend/datasage/api/v1/comparison.py), and [`saved.py`](file:///c:/Users/siddi/DataSage/backend/datasage/api/v1/saved.py) to return appropriate 404/422 errors instead of unhandled 500 crashes.
- Implemented [`backend/datasage/core/redis.py`](file:///c:/Users/siddi/DataSage/backend/datasage/core/redis.py) for asynchronous Redis caching and client management with automatic graceful offline fallback.
- Integrated Redis 24h caching into [`ValuationService`](file:///c:/Users/siddi/DataSage/backend/datasage/services/valuation_service.py) for fast sub-millisecond retrieval of computed property valuations.
- Added Redis connectivity detection to the `/health` endpoint and graceful pool shutdown in application lifespan.


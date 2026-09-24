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
- **Backend Type Safety & Database Integrity**:
  - Fixed variable shadowing of `select` in [`seed.py`](file:///c:/Users/siddi/DataSage/backend/datasage/cli/seed.py).
  - Fixed double cursor consumption in [`interaction_repo.py`](file:///c:/Users/siddi/DataSage/backend/datasage/repositories/interaction_repo.py).
  - Fixed string attribute access in [`comparison_service.py`](file:///c:/Users/siddi/DataSage/backend/datasage/services/comparison_service.py).
  - Fixed `PropertySummaryResponse` schema instantiation and null safety in [`recommendation_service.py`](file:///c:/Users/siddi/DataSage/backend/datasage/services/recommendation_service.py).
  - Added baseline `ModelVersion` seeding to prevent Foreign Key violations on heuristic predictions.


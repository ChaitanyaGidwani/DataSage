'use client';

import { Suspense, useEffect, useState, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import PropertyCard from '@/components/property/PropertyCard';
import { Icon } from '@/components/ui/Icon';
import styles from './page.module.css';

interface PropertySummary {
  id: string;
  title: string;
  property_type: string;
  bhk: number;
  area_sqft: number;
  listing_price: number;
  locality: { id: number; name: string; city: string };
  primary_image_url: string | null;
  valuation_summary: { pricing_classification: string | null } | null;
  location_score: number | null;
}

interface SearchResponse {
  data: PropertySummary[];
  pagination: { next_cursor: string | null; has_more: boolean; total_count: number };
}

export default function PropertiesPage() {
  return (
    <Suspense
      fallback={
        <div className={styles.page}>
          <div className="container">
            <div className={styles.grid}>
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className={`skeleton ${styles.skeleton}`} />
              ))}
            </div>
          </div>
        </div>
      }
    >
      <PropertiesContent />
    </Suspense>
  );
}

function PropertiesContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [properties, setProperties] = useState<PropertySummary[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [nextCursor, setNextCursor] = useState<string | null>(null);

  // Search & Filter state
  const [query, setQuery] = useState(searchParams.get('q') || searchParams.get('query') || '');
  const [cityId, setCityId] = useState(searchParams.get('city_id') || '');
  const [bhk, setBhk] = useState(searchParams.get('bhk') || '');
  const [minPrice, setMinPrice] = useState(searchParams.get('min_price') || '');
  const [maxPrice, setMaxPrice] = useState(searchParams.get('max_price') || '');
  const [propertyType, setPropertyType] = useState(searchParams.get('property_type') || '');
  const [pricingClassification, setPricingClassification] = useState(
    searchParams.get('pricing_classification') || ''
  );
  const [sortOption, setSortOption] = useState(searchParams.get('sort') || 'relevance');

  // Sync state when URL params change
  useEffect(() => {
    setQuery(searchParams.get('q') || searchParams.get('query') || '');
    setCityId(searchParams.get('city_id') || '');
    setBhk(searchParams.get('bhk') || '');
    setMinPrice(searchParams.get('min_price') || '');
    setMaxPrice(searchParams.get('max_price') || '');
    setPropertyType(searchParams.get('property_type') || '');
    setPricingClassification(searchParams.get('pricing_classification') || '');
    setSortOption(searchParams.get('sort') || 'relevance');
  }, [searchParams]);

  const fetchProperties = useCallback(
    async (cursor?: string) => {
      setLoading(true);
      try {
        const params = new URLSearchParams();
        if (query.trim()) params.set('q', query.trim());
        if (cityId) params.set('city_id', cityId);
        if (bhk) params.set('bhk', bhk);
        if (minPrice) params.set('min_price', minPrice);
        if (maxPrice) params.set('max_price', maxPrice);
        if (propertyType) params.set('property_type', propertyType);
        if (pricingClassification) params.set('pricing_classification', pricingClassification);

        // Map sort
        if (sortOption === 'price_asc') {
          params.set('sort', 'listing_price');
          params.set('order', 'asc');
        } else if (sortOption === 'price_desc') {
          params.set('sort', 'listing_price');
          params.set('order', 'desc');
        } else if (sortOption === 'area_desc') {
          params.set('sort', 'area_sqft');
          params.set('order', 'desc');
        } else if (sortOption === 'location_desc') {
          params.set('sort', 'cached_location_score');
          params.set('order', 'desc');
        } else {
          params.set('sort', 'relevance');
          params.set('order', 'desc');
        }

        if (cursor) params.set('cursor', cursor);
        params.set('limit', '20');

        const response = await api.get<SearchResponse>(`/properties?${params.toString()}`);
        const items = Array.isArray(response?.data) ? response.data : [];
        if (cursor) {
          setProperties((prev) => [...prev, ...items]);
        } else {
          setProperties(items);
        }
        setTotalCount(response?.pagination?.total_count ?? items.length);
        setNextCursor(response?.pagination?.next_cursor ?? null);
      } catch {
        // Error handled by API client
      } finally {
        setLoading(false);
      }
    },
    [query, cityId, bhk, minPrice, maxPrice, propertyType, pricingClassification, sortOption]
  );

  useEffect(() => {
    fetchProperties();
  }, [fetchProperties]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateUrlParams();
  };

  const updateUrlParams = () => {
    const params = new URLSearchParams();
    if (query.trim()) params.set('q', query.trim());
    if (cityId) params.set('city_id', cityId);
    if (bhk) params.set('bhk', bhk);
    if (minPrice) params.set('min_price', minPrice);
    if (maxPrice) params.set('max_price', maxPrice);
    if (propertyType) params.set('property_type', propertyType);
    if (pricingClassification) params.set('pricing_classification', pricingClassification);
    if (sortOption !== 'relevance') params.set('sort', sortOption);
    router.push(`/properties?${params.toString()}`);
  };

  const handleClearFilters = () => {
    setQuery('');
    setCityId('');
    setBhk('');
    setMinPrice('');
    setMaxPrice('');
    setPropertyType('');
    setPricingClassification('');
    setSortOption('relevance');
    router.push('/properties');
  };

  const handleLoadMore = () => {
    if (nextCursor) {
      fetchProperties(nextCursor);
    }
  };

  return (
    <div className={styles.page}>
      <div className="container">
        {/* Top Search Bar */}
        <div className={styles.searchBarContainer}>
          <form onSubmit={handleSearchSubmit} className={styles.searchBar}>
            <span className={styles.searchIconInside}>
              <Icon name="search" size={20} />
            </span>
            <input
              type="text"
              className={styles.searchInput}
              placeholder="Search by society, locality, or builder (e.g. Shipra Suncity, DLF Phase 2, Tata Primanti)..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            {query && (
              <button
                type="button"
                className={styles.clearSearchBtn}
                onClick={() => {
                  setQuery('');
                  const params = new URLSearchParams(searchParams.toString());
                  params.delete('q');
                  params.delete('query');
                  router.push(`/properties?${params.toString()}`);
                }}
                title="Clear search"
              >
                <Icon name="x" size={16} />
              </button>
            )}
            <button type="submit" className="btn btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
              <Icon name="search" size={16} /> Search
            </button>
          </form>

          {/* Quick chips */}
          <div className={styles.quickPresetsRow}>
            <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)' }}>Suggestions:</span>
            {['Shipra Suncity', 'Tata Primanti', 'Godrej', 'DLF Phase 2', 'Suncity Heights', 'Indirapuram'].map((chip) => (
              <button
                key={chip}
                type="button"
                className={styles.quickPresetBtn}
                onClick={() => {
                  setQuery(chip);
                  const params = new URLSearchParams(searchParams.toString());
                  params.set('q', chip);
                  router.push(`/properties?${params.toString()}`);
                }}
              >
                {chip}
              </button>
            ))}
          </div>
        </div>

        <div className={styles.layout}>
          {/* Filters sidebar */}
          <aside className={styles.sidebar}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-6)' }}>
              <h2 className={styles.sidebarTitle} style={{ margin: 0 }}>Filters</h2>
              {(query || cityId || bhk || minPrice || maxPrice || propertyType || pricingClassification) && (
                <button
                  onClick={handleClearFilters}
                  className="btn btn-ghost btn-sm"
                  style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-primary-400)', padding: 0 }}
                >
                  Reset All
                </button>
              )}
            </div>

            {/* City Filter */}
            <div className={styles.filterGroup}>
              <label className="input-label">City / Region</label>
              <select
                className="input"
                value={cityId}
                onChange={(e) => {
                  setCityId(e.target.value);
                }}
              >
                <option value="">All NCR Cities</option>
                <option value="2">Gurgaon</option>
                <option value="3">New Delhi</option>
                <option value="4">Ghaziabad (Indirapuram)</option>
                <option value="1">Noida</option>
                <option value="5">Greater Noida</option>
                <option value="6">Faridabad</option>
              </select>
            </div>

            {/* Valuation AI Status */}
            <div className={styles.filterGroup}>
              <label className="input-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Icon name="sparkles" size={14} /> AI Pricing Status
              </label>
              <div className={styles.valuationFilterGroup}>
                {[
                  { id: '', label: 'All' },
                  { id: 'underpriced', label: 'Underpriced (Deals)' },
                  { id: 'fair', label: 'Fair Price' },
                  { id: 'overpriced', label: 'Overpriced' },
                ].map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    className={`${styles.valuationBtn} ${
                      pricingClassification === item.id ? styles.valuationActive : ''
                    } ${item.id === 'underpriced' ? styles.valuationUnderpriced : ''} ${
                      item.id === 'overpriced' ? styles.valuationOverpriced : ''
                    }`}
                    onClick={() => {
                      setPricingClassification(item.id);
                    }}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>

            {/* BHK Filter */}
            <div className={styles.filterGroup}>
              <label className="input-label">BHK</label>
              <div className={styles.bhkGrid}>
                {['', '1', '2', '3', '4', '5'].map((val) => (
                  <button
                    key={val}
                    type="button"
                    className={`${styles.bhkBtn} ${bhk === val ? styles.bhkActive : ''}`}
                    onClick={() => setBhk(val)}
                  >
                    {val ? `${val} BHK` : 'All'}
                  </button>
                ))}
              </div>
            </div>

            {/* Price Range */}
            <div className={styles.filterGroup}>
              <label className="input-label">Price Range (₹)</label>
              <div className={styles.priceInputs}>
                <input
                  type="number"
                  className="input"
                  placeholder="Min ₹"
                  value={minPrice}
                  onChange={(e) => setMinPrice(e.target.value)}
                />
                <span className={styles.priceSep}>—</span>
                <input
                  type="number"
                  className="input"
                  placeholder="Max ₹"
                  value={maxPrice}
                  onChange={(e) => setMaxPrice(e.target.value)}
                />
              </div>
            </div>

            {/* Property Type */}
            <div className={styles.filterGroup}>
              <label className="input-label">Property Type</label>
              <select
                className="input"
                value={propertyType}
                onChange={(e) => setPropertyType(e.target.value)}
              >
                <option value="">All Types</option>
                <option value="apartment">Apartment</option>
                <option value="builder_floor">Builder Floor</option>
                <option value="house">House</option>
                <option value="plot">Plot</option>
              </select>
            </div>

            <button
              type="button"
              onClick={updateUrlParams}
              className="btn btn-primary"
              style={{ width: '100%', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
            >
              <Icon name="check" size={16} /> Apply Filters
            </button>
          </aside>

          {/* Results */}
          <div className={styles.results}>
            <div className={styles.resultsHeader}>
              <h1 className={styles.resultsTitle}>
                {loading
                  ? 'Searching Properties...'
                  : `${totalCount.toLocaleString()} Properties Found`}
                {query && (
                  <span style={{ fontSize: 'var(--fs-sm)', fontWeight: 'normal', color: 'var(--text-muted)', marginLeft: '8px' }}>
                    for &ldquo;{query}&rdquo;
                  </span>
                )}
              </h1>

              {/* Sort selector */}
              <div className={styles.resultsHeaderControls}>
                <label style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)' }}>Sort by:</label>
                <select
                  className={styles.sortSelect}
                  value={sortOption}
                  onChange={(e) => {
                    setSortOption(e.target.value);
                    const params = new URLSearchParams(searchParams.toString());
                    params.set('sort', e.target.value);
                    router.push(`/properties?${params.toString()}`);
                  }}
                >
                  <option value="relevance">Relevance / Newest</option>
                  <option value="price_asc">Price: Low to High</option>
                  <option value="price_desc">Price: High to Low</option>
                  <option value="area_desc">Area: Largest First</option>
                  <option value="location_desc">Top Location Score</option>
                </select>
              </div>
            </div>

            {loading && properties.length === 0 ? (
              <div className={styles.grid}>
                {Array.from({ length: 6 }).map((_, i) => (
                  <div key={i} className={`skeleton ${styles.skeleton}`} />
                ))}
              </div>
            ) : (
              <>
                <div className={styles.grid}>
                  {properties.map((prop) => (
                    <PropertyCard
                      key={prop.id}
                      id={prop.id}
                      title={prop.title}
                      propertyType={prop.property_type}
                      bhk={prop.bhk}
                      areaSqft={prop.area_sqft}
                      listingPrice={prop.listing_price}
                      locality={prop.locality.name}
                      city={prop.locality.city}
                      imageUrl={prop.primary_image_url}
                      pricingClassification={prop.valuation_summary?.pricing_classification}
                      locationScore={prop.location_score}
                    />
                  ))}
                </div>

                {nextCursor && (
                  <div className={styles.loadMore}>
                    <button
                      onClick={handleLoadMore}
                      className="btn btn-secondary"
                      disabled={loading}
                      style={{ minWidth: '180px' }}
                    >
                      {loading ? 'Loading...' : 'Load More Properties'}
                    </button>
                  </div>
                )}

                {!loading && properties.length === 0 && (
                  <div className={styles.empty}>
                    <span
                      className={styles.emptyIcon}
                      style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                    >
                      <Icon name="search" size={48} />
                    </span>
                    <h3 style={{ marginBottom: '8px' }}>No properties match your search</h3>
                    <p className={styles.emptyText}>
                      Try broadening your search terms or clearing price and configuration filters.
                    </p>
                    <button onClick={handleClearFilters} className="btn btn-secondary">
                      Clear All Filters
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

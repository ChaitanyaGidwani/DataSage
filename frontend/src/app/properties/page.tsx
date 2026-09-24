'use client';

import { Suspense, useEffect, useState, useCallback } from 'react';
import { useSearchParams } from 'next/navigation';
import { api } from '@/lib/api';
import PropertyCard from '@/components/property/PropertyCard';
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
    <Suspense fallback={<div className={styles.page}><div className="container"><div className={styles.grid}>{Array.from({ length: 6 }).map((_, i) => (<div key={i} className={`skeleton ${styles.skeleton}`} />))}</div></div></div>}>
      <PropertiesContent />
    </Suspense>
  );
}

function PropertiesContent() {
  const searchParams = useSearchParams();
  const [properties, setProperties] = useState<PropertySummary[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [nextCursor, setNextCursor] = useState<string | null>(null);

  // Filter state
  const [bhk, setBhk] = useState(searchParams.get('bhk') || '');
  const [minPrice, setMinPrice] = useState(searchParams.get('min_price') || '');
  const [maxPrice, setMaxPrice] = useState(searchParams.get('max_price') || '');
  const [propertyType, setPropertyType] = useState(searchParams.get('property_type') || '');

  const fetchProperties = useCallback(async (cursor?: string) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (bhk) params.set('bhk', bhk);
      if (minPrice) params.set('min_price', minPrice);
      if (maxPrice) params.set('max_price', maxPrice);
      if (propertyType) params.set('property_type', propertyType);
      if (cursor) params.set('cursor', cursor);
      params.set('limit', '20');

      const response = await api.get<SearchResponse>(`/properties?${params.toString()}`);
      if (cursor) {
        setProperties((prev) => [...prev, ...response.data]);
      } else {
        setProperties(response.data);
      }
      setTotalCount(response.pagination.total_count);
      setNextCursor(response.pagination.next_cursor);
    } catch {
      // Error handled by API client
    } finally {
      setLoading(false);
    }
  }, [bhk, minPrice, maxPrice, propertyType]);

  useEffect(() => {
    let ignore = false;
    const fetchInitial = async () => {
      try {
        const params = new URLSearchParams();
        if (bhk) params.set('bhk', bhk);
        if (minPrice) params.set('min_price', minPrice);
        if (maxPrice) params.set('max_price', maxPrice);
        if (propertyType) params.set('property_type', propertyType);
        params.set('limit', '20');

        const response = await api.get<SearchResponse>(`/properties?${params.toString()}`);
        if (!ignore) {
          setProperties(response.data);
          setTotalCount(response.pagination.total_count);
          setNextCursor(response.pagination.next_cursor);
        }
      } catch {
        // Error handled by API client
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    };

    fetchInitial();
    return () => {
      ignore = true;
    };
  }, [bhk, minPrice, maxPrice, propertyType]);

  const handleFilter = () => {
    fetchProperties();
  };

  const handleLoadMore = () => {
    if (nextCursor) {
      fetchProperties(nextCursor);
    }
  };

  return (
    <div className={styles.page}>
      <div className="container">
        <div className={styles.layout}>
          {/* Filters sidebar */}
          <aside className={styles.sidebar}>
            <h2 className={styles.sidebarTitle}>Filters</h2>

            <div className={styles.filterGroup}>
              <label className="input-label">BHK</label>
              <div className={styles.bhkGrid}>
                {['', '1', '2', '3', '4', '5'].map((val) => (
                  <button
                    key={val}
                    className={`${styles.bhkBtn} ${bhk === val ? styles.bhkActive : ''}`}
                    onClick={() => setBhk(val)}
                  >
                    {val || 'All'}
                  </button>
                ))}
              </div>
            </div>

            <div className={styles.filterGroup}>
              <label className="input-label">Price Range (₹)</label>
              <div className={styles.priceInputs}>
                <input
                  type="number"
                  className="input"
                  placeholder="Min"
                  value={minPrice}
                  onChange={(e) => setMinPrice(e.target.value)}
                />
                <span className={styles.priceSep}>—</span>
                <input
                  type="number"
                  className="input"
                  placeholder="Max"
                  value={maxPrice}
                  onChange={(e) => setMaxPrice(e.target.value)}
                />
              </div>
            </div>

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

            <button onClick={handleFilter} className="btn btn-primary" style={{ width: '100%' }}>
              Apply Filters
            </button>
          </aside>

          {/* Results */}
          <div className={styles.results}>
            <div className={styles.resultsHeader}>
              <h1 className={styles.resultsTitle}>
                {loading ? 'Searching...' : `${totalCount.toLocaleString()} Properties Found`}
              </h1>
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
                    <button onClick={handleLoadMore} className="btn btn-secondary" disabled={loading}>
                      {loading ? 'Loading...' : 'Load More'}
                    </button>
                  </div>
                )}

                {!loading && properties.length === 0 && (
                  <div className={styles.empty}>
                    <span className={styles.emptyIcon}>🔍</span>
                    <p className={styles.emptyText}>No properties match your filters</p>
                    <button onClick={() => { setBhk(''); setMinPrice(''); setMaxPrice(''); setPropertyType(''); handleFilter(); }} className="btn btn-ghost">
                      Clear Filters
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

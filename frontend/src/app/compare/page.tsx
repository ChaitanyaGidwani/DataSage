'use client';

import { Suspense, useEffect, useState, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import { formatINR, formatFurnishing } from '@/lib/formatters';
import { useCompare } from '@/contexts/CompareContext';
import { Icon, IconName } from '@/components/ui/Icon';
import styles from './page.module.css';

interface ComparedProperty {
  id: string;
  title: string;
  locality: string;
  city: string;
  property_type: string;
  bhk: number;
  area_sqft: number;
  listing_price: number;
  price_per_sqft: number;
  floor_info: string;
  facing: string | null;
  furnishing: string | null;
  parking_count: number;
  location_score: number;
  investment_score: number;
  estimated_rental_yield_pct: number;
  pricing_classification: string | null;
  predicted_value: number | null;
  key_advantages: string[];
  key_tradeoffs: string[];
  images?: string[];
}

interface ComparisonSummary {
  best_value_pick_id: string | null;
  best_location_pick_id: string | null;
  cheapest_per_sqft_id: string | null;
  highest_investment_pick_id: string | null;
  trade_off_summary?: string;
}

interface CompareResponse {
  properties: ComparedProperty[];
  summary: ComparisonSummary;
}

interface SearchItem {
  id: string;
  title: string;
  listing_price: number;
  bhk: number;
  locality: { name: string; city: string };
  valuation_summary?: { pricing_classification: string | null };
}

export default function ComparePage() {
  return (
    <Suspense
      fallback={
        <div className={styles.page}>
          <div className="container">
            <div className="skeleton" style={{ height: 400 }} />
          </div>
        </div>
      }
    >
      <CompareContent />
    </Suspense>
  );
}

function CompareContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { compareIds, addToCompare, removeFromCompare, clearCompare } = useCompare();

  const idsParam = searchParams.get('ids');
  const currentIds = idsParam ? idsParam.split(',').filter(Boolean) : compareIds;

  const [data, setData] = useState<CompareResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [copyToast, setCopyToast] = useState(false);

  // Property search state for adding to comparison
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchItem[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  // Auto-sync query param with context if idsParam is missing but context has ids
  useEffect(() => {
    if (!idsParam && compareIds.length >= 2) {
      router.replace(`/compare?ids=${compareIds.join(',')}`);
    }
  }, [idsParam, compareIds, router]);

  // Fetch comparison data
  const fetchComparison = useCallback(async (idsToFetch: string[]) => {
    if (idsToFetch.length < 2) {
      setData(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError('');
    try {
      const result = await api.get<CompareResponse>(`/comparison?ids=${idsToFetch.join(',')}`);
      setData(result);
      // Sync into context so navbar counter matches
      idsToFetch.forEach((id) => addToCompare(id));
    } catch {
      setError('Unable to load comparison for the selected properties.');
    } finally {
      setLoading(false);
    }
  }, [addToCompare]);

  useEffect(() => {
    if (currentIds.length >= 2) {
      fetchComparison(currentIds);
    } else {
      setLoading(false);
    }
  }, [idsParam]);

  // Search properties for quick add
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      setDropdownOpen(false);
      return;
    }

    const timer = setTimeout(async () => {
      setSearchLoading(true);
      try {
        const res = await api.get<{ data: SearchItem[] }>(`/properties?q=${encodeURIComponent(searchQuery.trim())}&limit=5`);
        setSearchResults(Array.isArray(res?.data) ? res.data : []);
        setDropdownOpen(true);
      } catch {
        setSearchResults([]);
      } finally {
        setSearchLoading(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  const handleAddProperty = (propId: string) => {
    if (currentIds.includes(propId)) return;
    if (currentIds.length >= 4) {
      alert('You can compare a maximum of 4 properties at once.');
      return;
    }
    const newIds = [...currentIds, propId];
    addToCompare(propId);
    setSearchQuery('');
    setDropdownOpen(false);
    router.push(`/compare?ids=${newIds.join(',')}`);
  };

  const handleRemoveProperty = (propId: string) => {
    const newIds = currentIds.filter((id) => id !== propId);
    removeFromCompare(propId);
    if (newIds.length >= 2) {
      router.push(`/compare?ids=${newIds.join(',')}`);
    } else if (newIds.length === 1) {
      router.push(`/compare?ids=${newIds[0]}`);
    } else {
      router.push('/compare');
    }
  };

  const handleLoadPreset = (presetIds: string[]) => {
    presetIds.forEach((id) => addToCompare(id));
    router.push(`/compare?ids=${presetIds.join(',')}`);
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopyToast(true);
    setTimeout(() => setCopyToast(false), 2500);
  };

  if (loading) {
    return (
      <div className={styles.page}>
        <div className="container">
          <div className={styles.header}>
            <div className={`skeleton ${styles.skeleton}`} style={{ height: 48, width: 320, marginBottom: 8 }} />
            <div className={`skeleton ${styles.skeleton}`} style={{ height: 20, width: 220 }} />
          </div>
          <div className={styles.matrix}>
            {currentIds.map((id) => (
              <div key={id} className={`skeleton ${styles.skeleton}`} style={{ height: 500 }} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  // When fewer than 2 properties are selected
  if (currentIds.length < 2 || !data) {
    return (
      <div className={styles.page}>
        <div className="container">
          <div className={styles.emptyState}>
            <span className={styles.emptyIcon} style={{ display: 'flex', justifyContent: 'center' }}>
              <Icon name="scale" size={54} />
            </span>
            <h1 className={styles.emptyTitle}>
              {currentIds.length === 1 ? 'Select a Second Property to Compare' : 'Property Comparison Matrix'}
            </h1>
            <p className={styles.emptyText}>
              {currentIds.length === 1
                ? 'You have 1 property selected. Search and add 1 to 3 more properties to benchmark side-by-side.'
                : 'Select 2 to 4 properties to view a normalized side-by-side analytical assessment with AI valuations, rental yields, and trade-offs.'}
            </p>

            {/* Live Search & Add */}
            <div className={styles.compareSearchWrapper}>
              <span className={styles.compareSearchIcon}>
                <Icon name="search" size={18} />
              </span>
              <input
                type="text"
                className={styles.compareSearchInput}
                placeholder="Search by name, locality, or builder (e.g. Shipra, Godrej, Tata)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => searchResults.length > 0 && setDropdownOpen(true)}
              />

              {dropdownOpen && searchResults.length > 0 && (
                <div className={styles.searchDropdown}>
                  {searchResults.map((item) => (
                    <div
                      key={item.id}
                      className={styles.searchDropdownItem}
                      onClick={() => handleAddProperty(item.id)}
                    >
                      <div>
                        <div className={styles.searchItemTitle}>{item.title}</div>
                        <div className={styles.searchItemSub}>
                          {item.bhk} BHK · {item.locality.name}, {item.locality.city} · {formatINR(item.listing_price)}
                        </div>
                      </div>
                      <button className="btn btn-primary btn-sm" style={{ pointerEvents: 'none' }}>
                        + Compare
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Quick 1-Click Comparison Presets */}
            <div className={styles.presetsSection}>
              <h3 className={styles.presetsTitle}>Or Explore Popular Comparison Scenarios</h3>
              <div className={styles.presetsGrid}>
                <div
                  className={styles.presetCard}
                  onClick={() =>
                    handleLoadPreset([
                      'a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d',
                      'f24cd120-abaa-43da-9395-1edde18da205',
                      '7cb1a4ec-b076-49be-b01a-909a7af33fd3',
                    ])
                  }
                >
                  <div className={styles.presetName}>
                    <Icon name="award" size={16} /> Shipra Suncity vs Godrej vs Suncity Heights
                  </div>
                  <div className={styles.presetDesc}>
                    NCR Value vs Luxury: 3 BHK in Indirapuram (₹85L) vs Sohna Road (₹1.75Cr) vs Golf Course Rd (₹3.25Cr).
                  </div>
                </div>

                <div
                  className={styles.presetCard}
                  onClick={() =>
                    handleLoadPreset([
                      'fb6602fe-848d-44c4-920f-6c2ab717423c',
                      'f24cd120-abaa-43da-9395-1edde18da205',
                      'ef47375a-5cad-4475-a478-f393fbf99e94',
                    ])
                  }
                >
                  <div className={styles.presetName}>
                    <Icon name="scale" size={16} /> Gurgaon Luxury Corridor Benchmark
                  </div>
                  <div className={styles.presetDesc}>
                    Tata Primanti (DLF Phase 2) vs Godrej Nature Plus (Sohna Rd) vs Ild Grand (Sector 49).
                  </div>
                </div>
              </div>
            </div>

            <div style={{ marginTop: 'var(--space-8)' }}>
              <Link href="/properties" className="btn btn-secondary">
                <Icon name="search" size={16} /> Browse All 4,500+ Properties
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const properties = Array.isArray(data?.properties) ? data.properties : [];
  const summary = data?.summary || {
    best_value_id: null,
    lowest_price_per_sqft_id: null,
    highest_appreciation_id: null,
    best_rental_yield_id: null,
  };
  const colClass =
    properties.length === 2
      ? styles.matrix2
      : properties.length === 3
        ? styles.matrix3
        : styles.matrix4;

  const getWinnerTag = (id: string): { label: string; icon: IconName } | null => {
    if (summary.best_value_pick_id === id) return { label: 'Best Value Pick', icon: 'award' };
    if (summary.best_location_pick_id === id) return { label: 'Top Location Score', icon: 'pin' };
    if (summary.cheapest_per_sqft_id === id) return { label: 'Lowest Rate/sqft', icon: 'tag' };
    if (summary.highest_investment_pick_id === id) return { label: 'Top Investment', icon: 'trendingUp' };
    return null;
  };

  return (
    <div className={styles.page}>
      <div className="container">
        {/* Header with Share and Actions */}
        <div className={styles.header} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 'var(--space-4)' }}>
          <div>
            <h1 className={styles.title}>
              Property <span className="gradient-text">Comparison Matrix</span>
            </h1>
            <p className={styles.subtitle}>
              Normalized multi-dimensional assessment of {properties.length} selected properties
            </p>
          </div>

          <div style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'center' }}>
            <button
              onClick={handleCopyLink}
              className="btn btn-secondary btn-sm"
              style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
            >
              <Icon name="check" size={14} /> {copyToast ? 'Link Copied!' : 'Share Comparison'}
            </button>
            <button
              onClick={() => {
                clearCompare();
                router.push('/compare');
              }}
              className="btn btn-ghost btn-sm"
            >
              Clear All
            </button>
          </div>
        </div>

        {/* Quick Add Search Bar inside active matrix */}
        {properties.length < 4 && (
          <div className={styles.compareSearchWrapper} style={{ margin: '0 0 var(--space-6) 0' }}>
            <span className={styles.compareSearchIcon}>
              <Icon name="search" size={16} />
            </span>
            <input
              type="text"
              className={styles.compareSearchInput}
              placeholder="+ Add another property to this comparison (e.g. Shipra, Godrej, Tata)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => searchResults.length > 0 && setDropdownOpen(true)}
            />

            {dropdownOpen && searchResults.length > 0 && (
              <div className={styles.searchDropdown}>
                {searchResults.map((item) => (
                  <div
                    key={item.id}
                    className={styles.searchDropdownItem}
                    onClick={() => handleAddProperty(item.id)}
                  >
                    <div>
                      <div className={styles.searchItemTitle}>{item.title}</div>
                      <div className={styles.searchItemSub}>
                        {item.bhk} BHK · {item.locality.name}, {item.locality.city} · {formatINR(item.listing_price)}
                      </div>
                    </div>
                    <button className="btn btn-primary btn-sm" style={{ pointerEvents: 'none' }}>
                      + Add
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Summary badges */}
        <div className={styles.summaryRow}>
          {summary.best_value_pick_id && (
            <div className={styles.summaryBadge}>
              <span className={styles.badgeIcon} style={{ display: 'flex', alignItems: 'center' }}>
                <Icon name="award" size={20} />
              </span>
              <div>
                <span className={styles.badgeLabel}>Best Value Pick</span>
                <br />
                <span className={styles.badgeValue}>
                  {properties.find((p) => p.id === summary.best_value_pick_id)?.locality}
                </span>
              </div>
            </div>
          )}
          {summary.best_location_pick_id && (
            <div className={styles.summaryBadge}>
              <span className={styles.badgeIcon} style={{ display: 'flex', alignItems: 'center' }}>
                <Icon name="pin" size={20} />
              </span>
              <div>
                <span className={styles.badgeLabel}>Top Location Score</span>
                <br />
                <span className={styles.badgeValue}>
                  {properties.find((p) => p.id === summary.best_location_pick_id)?.locality}
                </span>
              </div>
            </div>
          )}
          {summary.cheapest_per_sqft_id && (
            <div className={styles.summaryBadge}>
              <span className={styles.badgeIcon} style={{ display: 'flex', alignItems: 'center' }}>
                <Icon name="tag" size={20} />
              </span>
              <div>
                <span className={styles.badgeLabel}>Lowest Rate per sq ft</span>
                <br />
                <span className={styles.badgeValue}>
                  ₹{properties.find((p) => p.id === summary.cheapest_per_sqft_id)?.price_per_sqft.toLocaleString('en-IN')}/sqft
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Comparison matrix */}
        <div className={`${styles.matrix} ${colClass}`}>
          {properties.map((prop) => {
            const winner = getWinnerTag(prop.id);
            const primaryImg = prop.images && prop.images.length > 0 ? prop.images[0] : null;

            return (
              <div
                key={prop.id}
                className={`${styles.propertyCol} ${winner ? styles.winnerCol : ''}`}
              >
                {/* Remove button */}
                <button
                  className={styles.removeBtn}
                  onClick={() => handleRemoveProperty(prop.id)}
                  title="Remove from comparison"
                  aria-label="Remove property"
                >
                  <Icon name="x" size={14} />
                </button>

                {winner && (
                  <span className={styles.winnerTag} style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                    <Icon name={winner.icon} size={13} /> {winner.label}
                  </span>
                )}

                <div
                  className={styles.colHeader}
                  style={
                    primaryImg
                      ? {
                        backgroundImage: `url(${primaryImg})`,
                        backgroundSize: 'cover',
                        backgroundPosition: 'center',
                      }
                      : undefined
                  }
                >
                  {!primaryImg && (
                    <span className={styles.colHeaderIcon} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Icon name="building" size={26} />
                    </span>
                  )}
                </div>

                <div className={styles.colBody}>
                  <Link href={`/properties/${prop.id}`} style={{ textDecoration: 'none' }}>
                    <h3 className={styles.colTitle}>{prop.title}</h3>
                  </Link>
                  <p className={styles.colLocation} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Icon name="pin" size={13} /> {prop.locality}, {prop.city}
                  </p>

                  {prop.pricing_classification && (
                    <span className={`badge badge-${prop.pricing_classification} ${styles.priceBadge}`}>
                      {prop.pricing_classification === 'underpriced'
                        ? 'Underpriced'
                        : prop.pricing_classification === 'overpriced'
                          ? 'Overpriced'
                          : 'Fair Price'}
                    </span>
                  )}

                  <div className={styles.metricRow}>
                    <span className={styles.metricLabel}>Listing Price</span>
                    <span className={styles.metricValue}>{formatINR(prop.listing_price)}</span>
                  </div>
                  <div className={styles.metricRow}>
                    <span className={styles.metricLabel}>Price / sq ft</span>
                    <span className={`${styles.metricValue} ${summary.cheapest_per_sqft_id === prop.id ? styles.metricHighlight : ''}`}>
                      ₹{prop.price_per_sqft.toLocaleString('en-IN')}
                    </span>
                  </div>
                  <div className={styles.metricRow}>
                    <span className={styles.metricLabel}>Configuration</span>
                    <span className={styles.metricValue}>{prop.bhk} BHK</span>
                  </div>
                  <div className={styles.metricRow}>
                    <span className={styles.metricLabel}>Carpet Area</span>
                    <span className={styles.metricValue}>{prop.area_sqft.toLocaleString('en-IN')} sqft</span>
                  </div>
                  <div className={styles.metricRow}>
                    <span className={styles.metricLabel}>Location Score</span>
                    <span className={`${styles.metricValue} ${summary.best_location_pick_id === prop.id ? styles.metricHighlight : ''}`}>
                      {prop.location_score}/100
                    </span>
                  </div>
                  <div className={styles.metricRow}>
                    <span className={styles.metricLabel}>Investment Score</span>
                    <span className={styles.metricValue}>{prop.investment_score}/100</span>
                  </div>
                  <div className={styles.metricRow}>
                    <span className={styles.metricLabel}>Gross Rental Yield</span>
                    <span className={styles.metricValue}>{prop.estimated_rental_yield_pct.toFixed(1)}%</span>
                  </div>
                  {prop.predicted_value && (
                    <div className={styles.metricRow}>
                      <span className={styles.metricLabel}>AI Fair Value</span>
                      <span className={`${styles.metricValue} ${styles.metricHighlight}`}>
                        {formatINR(prop.predicted_value)}
                      </span>
                    </div>
                  )}
                  <div className={styles.metricRow}>
                    <span className={styles.metricLabel}>Floor Level</span>
                    <span className={styles.metricValue}>{prop.floor_info}</span>
                  </div>
                  <div className={styles.metricRow}>
                    <span className={styles.metricLabel}>Furnishing</span>
                    <span className={styles.metricValue}>{prop.furnishing ? formatFurnishing(prop.furnishing) : '—'}</span>
                  </div>

                  {(prop.key_advantages.length > 0 || prop.key_tradeoffs.length > 0) && (
                    <div className={styles.tagList}>
                      {prop.key_advantages.map((adv, i) => (
                        <span key={`adv-${i}`} className={styles.tagAdvantage} style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          <Icon name="check" size={12} /> {adv}
                        </span>
                      ))}
                      {prop.key_tradeoffs.map((t, i) => (
                        <span key={`t-${i}`} className={styles.tagTradeoff} style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          <Icon name="alert" size={12} /> {t}
                        </span>
                      ))}
                    </div>
                  )}

                  <div style={{ marginTop: 'var(--space-4)', paddingTop: 'var(--space-3)', borderTop: '1px solid var(--border-color)', textAlign: 'center' }}>
                    <Link
                      href={`/properties/${prop.id}`}
                      className="btn btn-secondary btn-sm"
                      style={{ width: '100%', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
                    >
                      View Intelligence <Icon name="arrowRight" size={12} />
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div style={{ textAlign: 'center', marginTop: 'var(--space-8)', display: 'flex', justifyContent: 'center', gap: 'var(--space-3)' }}>
          <Link href="/properties" className="btn btn-secondary">
            <Icon name="search" size={16} /> Search More Properties
          </Link>
        </div>
      </div>
    </div>
  );
}

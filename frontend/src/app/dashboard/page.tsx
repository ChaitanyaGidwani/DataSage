'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';
import { formatDate, formatINR, formatArea } from '@/lib/formatters';
import { Icon } from '@/components/ui/Icon';
import styles from './page.module.css';

interface SavedPropertyItem {
  id: string;
  property_id: string;
  created_at: string;
  title?: string | null;
  listing_price?: number | null;
  bhk?: number | null;
  area_sqft?: number | null;
  property_type?: string | null;
  locality_name?: string | null;
  city_name?: string | null;
  notes?: string | null;
}

interface SearchHistoryItem {
  id: string;
  query_params?: Record<string, unknown>;
  search_params?: Record<string, unknown>;
  result_count: number;
  created_at: string;
}

interface RecommendationItem {
  property: {
    id: string;
    title: string;
    listing_price: number;
    bhk: number;
    area_sqft: number;
    property_type: string;
    locality?: { id: number; name: string; city: string };
    pricing_classification?: string | null;
  };
  suitability_score: number;
  match_reasons: string[];
}

export default function DashboardPage() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  const [savedProperties, setSavedProperties] = useState<SavedPropertyItem[]>([]);
  const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([]);
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated) {
      Promise.all([
        api.get<any>('/saved-properties').catch(() => ({ data: [] })),
        api.get<any>('/search-history').catch(() => ({ data: [] })),
        api.get<any>('/recommendations?limit=3').catch(() => ({ items: [] })),
      ])
        .then(([savedRes, historyRes, recRes]) => {
          const savedList = Array.isArray(savedRes)
            ? savedRes
            : Array.isArray(savedRes?.data)
            ? savedRes.data
            : [];
          const historyList = Array.isArray(historyRes)
            ? historyRes
            : Array.isArray(historyRes?.data)
            ? historyRes.data
            : [];
          const recList = Array.isArray(recRes?.items)
            ? recRes.items
            : Array.isArray(recRes)
            ? recRes
            : [];

          setSavedProperties(savedList);
          setSearchHistory(historyList);
          setRecommendations(recList);
        })
        .finally(() => setLoading(false));
    }
  }, [isAuthenticated]);

  const handleUnsave = async (e: React.MouseEvent, propertyId: string) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      await api.delete(`/saved-properties/${propertyId}`);
      setSavedProperties((prev) =>
        prev.filter((item) => item.property_id !== propertyId && item.id !== propertyId)
      );
    } catch {
      // ignore
    }
  };

  const handleClearHistory = async () => {
    try {
      await api.delete('/search-history');
      setSearchHistory([]);
    } catch {
      // ignore
    }
  };

  const getSearchUrl = (params?: Record<string, unknown>) => {
    if (!params) return '/properties';
    const urlParams = new URLSearchParams();
    if (params.q) urlParams.set('q', String(params.q));
    if (params.city_id) urlParams.set('city', String(params.city_id));
    if (params.bhk) urlParams.set('bhk', String(params.bhk));
    if (params.property_type) urlParams.set('type', String(params.property_type));
    if (params.pricing_classification) {
      urlParams.set('pricing', String(params.pricing_classification));
    }
    const query = urlParams.toString();
    return query ? `/properties?${query}` : '/properties';
  };

  if (isLoading || !isAuthenticated || loading) {
    return (
      <div className={styles.page}>
        <div className="container">
          <div className="skeleton" style={{ height: 350 }} />
        </div>
      </div>
    );
  }

  const safeSaved = Array.isArray(savedProperties) ? savedProperties : [];
  const safeHistory = Array.isArray(searchHistory) ? searchHistory : [];
  const safeRecs = Array.isArray(recommendations) ? recommendations : [];

  return (
    <div className={styles.page}>
      <div className="container">
        <div className={styles.header}>
          <h1 className={styles.title}>
            Welcome back, <span className="gradient-text">{user?.name}</span>
          </h1>
          <p className={styles.subtitle}>Your real estate intelligence portfolio and saved analysis</p>
        </div>

        {/* Stats row */}
        <div className={styles.statsRow}>
          <div className={styles.statCard}>
            <span className={styles.statIcon} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Icon name="bookmark" size={20} />
            </span>
            <div>
              <span className={styles.statNumber}>{safeSaved.length}</span>
              <span className={styles.statLabel}>Saved Listings</span>
            </div>
          </div>
          <div className={styles.statCard}>
            <span className={styles.statIcon} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Icon name="search" size={20} />
            </span>
            <div>
              <span className={styles.statNumber}>{safeHistory.length}</span>
              <span className={styles.statLabel}>Recent Searches</span>
            </div>
          </div>
          <div className={styles.statCard}>
            <span className={styles.statIcon} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Icon name="sparkles" size={20} />
            </span>
            <div>
              <span className={styles.statNumber}>Active</span>
              <span className={styles.statLabel}>AI Valuation Engine</span>
            </div>
          </div>
        </div>

        {/* AI Recommendations section if available */}
        {safeRecs.length > 0 && (
          <div className={styles.recSection}>
            <div className={styles.sectionHeader}>
              <h2 className={styles.sectionTitle} style={{ marginBottom: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Icon name="sparkles" size={18} /> Top AI Recommendations For You
              </h2>
              <Link href="/onboarding" className="btn btn-secondary btn-sm" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                <Icon name="sliders" size={14} /> Refine Preferences
              </Link>
            </div>
            <div className={styles.recGrid}>
              {safeRecs.map((rec) => (
                <Link
                  key={rec.property.id}
                  href={`/properties/${rec.property.id}`}
                  className={styles.recCard}
                >
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                      <span className="badge badge-success" style={{ fontSize: '11px' }}>
                        {rec.suitability_score}% Match
                      </span>
                      <span style={{ fontWeight: 600, color: 'var(--color-primary-400)' }}>
                        {formatINR(rec.property.listing_price)}
                      </span>
                    </div>
                    <h3 style={{ fontSize: 'var(--fs-sm)', fontWeight: 600, marginBottom: '4px' }}>
                      {rec.property.title}
                    </h3>
                    <p style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)', marginBottom: '8px' }}>
                      {rec.property.bhk} BHK · {formatArea(rec.property.area_sqft)} · {rec.property.locality?.name || 'Delhi-NCR'}
                    </p>
                  </div>
                  {rec.match_reasons && rec.match_reasons.length > 0 && (
                    <div style={{ fontSize: '11px', color: 'var(--text-secondary)', background: 'var(--bg-secondary)', padding: '6px 8px', borderRadius: '4px' }}>
                      ✓ {rec.match_reasons[0]}
                    </div>
                  )}
                </Link>
              ))}
            </div>
          </div>
        )}

        <div className={styles.grid}>
          {/* Saved Properties */}
          <section className={styles.section}>
            <div className={styles.sectionHeader}>
              <h2 className={styles.sectionTitle} style={{ marginBottom: 0 }}>Saved Properties</h2>
              {safeSaved.length > 0 && (
                <span className="badge badge-primary">{safeSaved.length} saved</span>
              )}
            </div>

            {safeSaved.length === 0 ? (
              <div className={styles.empty}>
                <p>No saved properties yet. Browse and track properties of interest.</p>
                <Link href="/properties" className="btn btn-primary btn-sm">
                  Browse Properties
                </Link>
              </div>
            ) : (
              <div className={styles.list}>
                {safeSaved.map((item) => (
                  <div
                    key={item.id}
                    className={styles.listItem}
                    style={{ position: 'relative' }}
                  >
                    <span className={styles.listIcon} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Icon name="building" size={18} />
                    </span>
                    <div className={styles.listContent}>
                      <div className={styles.listRow}>
                        <Link
                          href={`/properties/${item.property_id}`}
                          className={styles.listTitle}
                          style={{ textDecoration: 'none', color: 'inherit' }}
                        >
                          {item.title || 'Property Listing'}
                        </Link>
                        {item.listing_price ? (
                          <span className={styles.listPrice}>
                            {formatINR(item.listing_price)}
                          </span>
                        ) : null}
                      </div>
                      <div className={styles.listRow} style={{ marginTop: '2px' }}>
                        <span className={styles.listMeta}>
                          {item.bhk ? `${item.bhk} BHK` : ''}
                          {item.area_sqft ? ` · ${formatArea(item.area_sqft)}` : ''}
                          {item.locality_name ? ` · ${item.locality_name}` : ''}
                          {item.city_name ? `, ${item.city_name}` : ''}
                        </span>
                        <button
                          type="button"
                          className={styles.deleteBtn}
                          onClick={(e) => handleUnsave(e, item.property_id)}
                          title="Remove from saved"
                          aria-label="Remove from saved"
                        >
                          <Icon name="x" size={14} />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Search History */}
          <section className={styles.section}>
            <div className={styles.sectionHeader}>
              <h2 className={styles.sectionTitle} style={{ marginBottom: 0 }}>Recent Searches</h2>
              {safeHistory.length > 0 && (
                <button
                  type="button"
                  className={styles.clearBtn}
                  onClick={handleClearHistory}
                  title="Clear all search history"
                >
                  Clear History
                </button>
              )}
            </div>

            {safeHistory.length === 0 ? (
              <div className={styles.empty}>
                <p>No search history yet. Explore Delhi-NCR micro-markets.</p>
                <Link href="/properties" className="btn btn-primary btn-sm">
                  Start Exploring
                </Link>
              </div>
            ) : (
              <div className={styles.list}>
                {safeHistory.map((item) => {
                  const params = item.query_params || item.search_params;
                  const searchUrl = getSearchUrl(params);
                  const q = params?.q as string | undefined;
                  const bhk = params?.bhk as string | number | undefined;

                  return (
                    <Link
                      key={item.id}
                      href={searchUrl}
                      className={styles.listItem}
                    >
                      <span className={styles.listIcon} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Icon name="search" size={18} />
                      </span>
                      <div className={styles.listContent}>
                        <div className={styles.listRow}>
                          <span className={styles.listTitle}>
                            {q ? `Search: "${q}"` : `${item.result_count} listings found`}
                          </span>
                          <span className={styles.listMeta}>{formatDate(item.created_at)}</span>
                        </div>
                        <div style={{ marginTop: '4px' }}>
                          {q ? <span className={styles.historyTag}>Keyword: {String(q)}</span> : null}
                          {bhk ? <span className={styles.historyTag}>{String(bhk)} BHK</span> : null}
                          {params?.pricing_classification ? (
                            <span className={styles.historyTag}>
                              {String(params.pricing_classification)}
                            </span>
                          ) : null}
                          {!q && !bhk && !params?.pricing_classification ? (
                            <span className={styles.listMeta}>Explored NCR catalog</span>
                          ) : null}
                        </div>
                      </div>
                    </Link>
                  );
                })}
              </div>
            )}
          </section>
        </div>

        {/* Quick actions */}
        <div className={styles.actions}>
          <Link href="/properties" className="btn btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
            <Icon name="search" size={16} /> Search Properties
          </Link>
          <Link href="/compare" className="btn btn-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
            <Icon name="scale" size={16} /> Compare Properties
          </Link>
          <Link href="/onboarding" className="btn btn-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
            <Icon name="sparkles" size={16} /> AI Buyer Profile
          </Link>
        </div>
      </div>
    </div>
  );
}

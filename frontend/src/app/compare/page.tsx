'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import { formatINR, formatFurnishing } from '@/lib/formatters';
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
}

interface ComparisonSummary {
  best_value_pick_id: string | null;
  best_location_pick_id: string | null;
  cheapest_per_sqft_id: string | null;
  highest_investment_pick_id: string | null;
  trade_off_summary: string;
}

interface CompareResponse {
  properties: ComparedProperty[];
  summary: ComparisonSummary;
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
  const idsParam = searchParams.get('ids');
  const ids = idsParam ? idsParam.split(',').filter(Boolean) : [];

  const [data, setData] = useState<CompareResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (ids.length < 2) {
      setLoading(false);
      return;
    }

    const fetchComparison = async () => {
      setLoading(true);
      setError('');
      try {
        const result = await api.get<CompareResponse>(`/compare?ids=${ids.join(',')}`);
        setData(result);
      } catch {
        setError('Failed to load comparison data. Please check property IDs.');
      } finally {
        setLoading(false);
      }
    };

    fetchComparison();
  }, [idsParam]);

  if (loading) {
    return (
      <div className={styles.page}>
        <div className="container">
          <div className={styles.header}>
            <div className={`skeleton ${styles.skeleton}`} style={{ height: 48, width: 300, marginBottom: 8 }} />
            <div className={`skeleton ${styles.skeleton}`} style={{ height: 20, width: 200 }} />
          </div>
          <div className={styles.matrix}>
            {ids.map((id) => (
              <div key={id} className={`skeleton ${styles.skeleton}`} style={{ height: 500 }} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (ids.length < 2 || error || !data) {
    return (
      <div className={styles.page}>
        <div className="container">
          <div className={styles.emptyState}>
            <span className={styles.emptyIcon} style={{ display: 'flex', justifyContent: 'center' }}>
              <Icon name="scale" size={48} />
            </span>
            <h1 className={styles.emptyTitle}>
              {error || 'Select Properties to Compare'}
            </h1>
            <p className={styles.emptyText}>
              Add 2 to 4 properties from search results to see a normalized side-by-side analytical matrix.
            </p>
            <Link href="/properties" className="btn btn-primary">
              Browse Properties
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const { properties, summary } = data;
  const colClass =
    properties.length === 2
      ? styles.matrix2
      : properties.length === 3
      ? styles.matrix3
      : styles.matrix4;

  const getWinnerTag = (id: string): { label: string; icon: IconName } | null => {
    if (summary.best_value_pick_id === id) return { label: 'Best Value', icon: 'award' };
    if (summary.best_location_pick_id === id) return { label: 'Top Location', icon: 'pin' };
    if (summary.cheapest_per_sqft_id === id) return { label: 'Best Rate/sqft', icon: 'tag' };
    if (summary.highest_investment_pick_id === id) return { label: 'Top Investment', icon: 'trendingUp' };
    return null;
  };

  return (
    <div className={styles.page}>
      <div className="container">
        <div className={styles.header}>
          <h1 className={styles.title}>
            Property <span className="gradient-text">Comparison Matrix</span>
          </h1>
          <p className={styles.subtitle}>
            Normalized multi-dimensional assessment of {properties.length} selected properties
          </p>
        </div>

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
            return (
              <div
                key={prop.id}
                className={`${styles.propertyCol} ${winner ? styles.winnerCol : ''}`}
              >
                {winner && (
                  <span className={styles.winnerTag} style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                    <Icon name={winner.icon} size={13} /> {winner.label}
                  </span>
                )}

                <div className={styles.colHeader}>
                  <span className={styles.colHeaderIcon} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Icon name="building" size={26} />
                  </span>
                </div>

                <div className={styles.colBody}>
                  <h3 className={styles.colTitle}>{prop.title}</h3>
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
                </div>
              </div>
            );
          })}
        </div>

        <div style={{ textAlign: 'center', marginTop: 'var(--space-8)' }}>
          <Link href="/properties" className="btn btn-secondary">
            Back to Properties
          </Link>
        </div>
      </div>
    </div>
  );
}

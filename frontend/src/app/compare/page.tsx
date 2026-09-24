'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import { formatINR } from '@/lib/formatters';
import styles from './page.module.css';

interface ComparisonItem {
  id: string;
  title: string;
  city: string;
  locality: string;
  property_type: string;
  bhk: number;
  area_sqft: number;
  listing_price: number;
  price_per_sqft: number;
  floor_info: string;
  furnishing: string | null;
  facing: string | null;
  parking_count: number;
  construction_year: number | null;
  predicted_value: number | null;
  price_gap_pct: number | null;
  pricing_classification: string | null;
  valuation_confidence: number | null;
  location_score: number;
  investment_score: number;
  estimated_rental_yield_pct: number;
  key_advantages: string[];
  key_tradeoffs: string[];
}

interface ComparisonSummary {
  best_value_pick_id: string | null;
  best_value_reason: string | null;
  best_location_pick_id: string | null;
  best_location_reason: string | null;
  highest_investment_pick_id: string | null;
  cheapest_per_sqft_id: string | null;
}

interface ComparisonResponse {
  properties: ComparisonItem[];
  summary: ComparisonSummary;
}

export default function ComparePage() {
  return (
    <Suspense
      fallback={
        <div className={styles.page}>
          <div className="container">
            <div className={styles.loadingGrid}>
              <div className={`skeleton ${styles.skeleton}`} />
              <div className={`skeleton ${styles.skeleton}`} />
            </div>
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
  const [data, setData] = useState<ComparisonResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const idsParam = searchParams.get('ids') || '';
  const ids = idsParam
    .split(',')
    .map((id) => id.trim())
    .filter(Boolean);

  useEffect(() => {
    if (ids.length < 2) {
      setLoading(false);
      return;
    }

    const fetchComparison = async () => {
      try {
        const response = await api.post<ComparisonResponse>('/comparison', {
          property_ids: ids,
        });
        setData(response);
      } catch {
        setError('Failed to load comparison data');
      } finally {
        setLoading(false);
      }
    };

    fetchComparison();
  }, [idsParam]); // eslint-disable-line react-hooks/exhaustive-deps

  if (loading) {
    return (
      <div className={styles.page}>
        <div className="container">
          <div className={styles.loadingGrid}>
            {ids.map((id) => (
              <div key={id} className={`skeleton ${styles.skeleton}`} />
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
            <span className={styles.emptyIcon}>⚖️</span>
            <h1 className={styles.emptyTitle}>
              {error || 'Select properties to compare'}
            </h1>
            <p className={styles.emptyText}>
              Add 2 to 4 properties from the search results to see a side-by-side comparison.
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

  const getWinnerTag = (id: string): string | null => {
    if (summary.best_value_pick_id === id) return '🏆 Best Value';
    if (summary.best_location_pick_id === id) return '📍 Top Location';
    if (summary.cheapest_per_sqft_id === id) return '💰 Cheapest/sqft';
    if (summary.highest_investment_pick_id === id) return '📈 Best Investment';
    return null;
  };

  return (
    <div className={styles.page}>
      <div className="container">
        <div className={styles.header}>
          <h1 className={styles.title}>
            Property <span className="gradient-text">Comparison</span>
          </h1>
          <p className={styles.subtitle}>
            Side-by-side analysis of {properties.length} properties
          </p>
        </div>

        {/* Summary badges */}
        <div className={styles.summaryRow}>
          {summary.best_value_pick_id && (
            <div className={styles.summaryBadge}>
              <span className={styles.badgeIcon}>🏆</span>
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
              <span className={styles.badgeIcon}>📍</span>
              <div>
                <span className={styles.badgeLabel}>Top Location</span>
                <br />
                <span className={styles.badgeValue}>
                  {properties.find((p) => p.id === summary.best_location_pick_id)?.locality}
                </span>
              </div>
            </div>
          )}
          {summary.cheapest_per_sqft_id && (
            <div className={styles.summaryBadge}>
              <span className={styles.badgeIcon}>💰</span>
              <div>
                <span className={styles.badgeLabel}>Cheapest per sqft</span>
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
            const winnerTag = getWinnerTag(prop.id);
            return (
              <div
                key={prop.id}
                className={`${styles.propertyCol} ${winnerTag ? styles.winnerCol : ''}`}
              >
                {winnerTag && <span className={styles.winnerTag}>{winnerTag}</span>}

                <div className={styles.colHeader}>
                  <span className={styles.colHeaderIcon}>🏠</span>
                </div>

                <div className={styles.colBody}>
                  <h3 className={styles.colTitle}>{prop.title}</h3>
                  <p className={styles.colLocation}>
                    📍 {prop.locality}, {prop.city}
                  </p>

                  {prop.pricing_classification && (
                    <span className={`badge badge-${prop.pricing_classification} ${styles.priceBadge}`}>
                      {prop.pricing_classification === 'underpriced'
                        ? '▼ Underpriced'
                        : prop.pricing_classification === 'overpriced'
                        ? '▲ Overpriced'
                        : '● Fair Price'}
                    </span>
                  )}

                  <div className={styles.metricRow}>
                    <span className={styles.metricLabel}>Price</span>
                    <span className={styles.metricValue}>{formatINR(prop.listing_price)}</span>
                  </div>
                  <div className={styles.metricRow}>
                    <span className={styles.metricLabel}>Price/sqft</span>
                    <span className={`${styles.metricValue} ${summary.cheapest_per_sqft_id === prop.id ? styles.metricHighlight : ''}`}>
                      ₹{prop.price_per_sqft.toLocaleString('en-IN')}
                    </span>
                  </div>
                  <div className={styles.metricRow}>
                    <span className={styles.metricLabel}>BHK</span>
                    <span className={styles.metricValue}>{prop.bhk} BHK</span>
                  </div>
                  <div className={styles.metricRow}>
                    <span className={styles.metricLabel}>Area</span>
                    <span className={styles.metricValue}>{prop.area_sqft.toLocaleString('en-IN')} sqft</span>
                  </div>
                  <div className={styles.metricRow}>
                    <span className={styles.metricLabel}>Location Score</span>
                    <span className={`${styles.metricValue} ${summary.best_location_pick_id === prop.id ? styles.metricHighlight : ''}`}>
                      {prop.location_score}/100
                    </span>
                  </div>
                  <div className={styles.metricRow}>
                    <span className={styles.metricLabel}>Investment</span>
                    <span className={styles.metricValue}>{prop.investment_score}/100</span>
                  </div>
                  <div className={styles.metricRow}>
                    <span className={styles.metricLabel}>Rental Yield</span>
                    <span className={styles.metricValue}>{prop.estimated_rental_yield_pct.toFixed(1)}%</span>
                  </div>
                  {prop.predicted_value && (
                    <div className={styles.metricRow}>
                      <span className={styles.metricLabel}>AI Value</span>
                      <span className={`${styles.metricValue} ${styles.metricHighlight}`}>
                        {formatINR(prop.predicted_value)}
                      </span>
                    </div>
                  )}
                  <div className={styles.metricRow}>
                    <span className={styles.metricLabel}>Floor</span>
                    <span className={styles.metricValue}>{prop.floor_info}</span>
                  </div>
                  <div className={styles.metricRow}>
                    <span className={styles.metricLabel}>Furnishing</span>
                    <span className={styles.metricValue}>{prop.furnishing?.replace('_', ' ') || '—'}</span>
                  </div>

                  {(prop.key_advantages.length > 0 || prop.key_tradeoffs.length > 0) && (
                    <div className={styles.tagList}>
                      {prop.key_advantages.map((adv, i) => (
                        <span key={`adv-${i}`} className={styles.tagAdvantage}>
                          ✓ {adv}
                        </span>
                      ))}
                      {prop.key_tradeoffs.map((t, i) => (
                        <span key={`t-${i}`} className={styles.tagTradeoff}>
                          ⚠ {t}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        <div style={{ textAlign: 'center' }}>
          <Link href="/properties" className="btn btn-secondary">
            ← Back to Search
          </Link>
        </div>
      </div>
    </div>
  );
}

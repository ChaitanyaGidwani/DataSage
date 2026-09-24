'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import { formatINR, formatArea, formatPropertyType, formatDate, formatPercent } from '@/lib/formatters';
import styles from './page.module.css';

interface PropertyDetail {
  id: string;
  title: string;
  property_type: string;
  bhk: number;
  area_sqft: number;
  listing_price: number;
  floor_number: number | null;
  total_floors: number | null;
  facing: string | null;
  construction_year: number | null;
  furnishing: string | null;
  parking_count: number;
  balcony_count: number;
  bathroom_count: number | null;
  description: string | null;
  data_source: string;
  locality: { id: number; name: string; city: string };
  location: { latitude: number | null; longitude: number | null; full_address: string | null; pin_code: string | null } | null;
  images: Array<{ url: string; is_primary: boolean }>;
  listed_at: string | null;
  created_at: string;
}

export default function PropertyDetailPage() {
  const params = useParams();
  const [property, setProperty] = useState<PropertyDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchProperty = async () => {
      try {
        const data = await api.get<PropertyDetail>(`/properties/${params.id}`);
        setProperty(data);
      } catch {
        setError('Property not found');
      } finally {
        setLoading(false);
      }
    };
    fetchProperty();
  }, [params.id]);

  if (loading) {
    return (
      <div className={styles.page}>
        <div className="container">
          <div className={`skeleton ${styles.heroSkeleton}`} />
          <div className={`skeleton ${styles.detailSkeleton}`} />
        </div>
      </div>
    );
  }

  if (error || !property) {
    return (
      <div className={styles.page}>
        <div className={`container ${styles.errorState}`}>
          <span className={styles.errorIcon}>🏚️</span>
          <h1>Property not found</h1>
          <p>This property may have been removed or the link is incorrect.</p>
        </div>
      </div>
    );
  }

  const pricePerSqft = Math.round(property.listing_price / property.area_sqft);

  return (
    <div className={styles.page}>
      <div className="container">
        {/* Image gallery placeholder */}
        <div className={styles.gallery}>
          <div className={styles.galleryMain}>
            <span className={styles.galleryIcon}>🏠</span>
          </div>
        </div>

        <div className={styles.content}>
          {/* Main info */}
          <div className={styles.mainInfo}>
            <div className={styles.priceRow}>
              <span className={styles.price}>{formatINR(property.listing_price)}</span>
              <span className={styles.pricePerSqft}>₹{pricePerSqft.toLocaleString('en-IN')}/sq ft</span>
            </div>

            <h1 className={styles.title}>{property.title}</h1>

            <div className={styles.location}>
              📍 {property.locality.name}, {property.locality.city}
              {property.location?.pin_code && ` — ${property.location.pin_code}`}
            </div>

            {/* Specs grid */}
            <div className={styles.specsGrid}>
              <SpecItem label="BHK" value={`${property.bhk}`} />
              <SpecItem label="Area" value={formatArea(property.area_sqft)} />
              <SpecItem label="Type" value={formatPropertyType(property.property_type)} />
              {property.floor_number != null && (
                <SpecItem label="Floor" value={`${property.floor_number}/${property.total_floors || '—'}`} />
              )}
              {property.facing && <SpecItem label="Facing" value={property.facing} />}
              {property.construction_year && <SpecItem label="Built" value={`${property.construction_year}`} />}
              {property.furnishing && (
                <SpecItem label="Furnishing" value={property.furnishing.replace('_', ' ')} />
              )}
              <SpecItem label="Parking" value={`${property.parking_count}`} />
              <SpecItem label="Balconies" value={`${property.balcony_count}`} />
              {property.bathroom_count != null && (
                <SpecItem label="Bathrooms" value={`${property.bathroom_count}`} />
              )}
            </div>

            {/* Description */}
            {property.description && (
              <div className={styles.descriptionSection}>
                <h2 className={styles.sectionTitle}>About this property</h2>
                <p className={styles.description}>{property.description}</p>
              </div>
            )}

            {/* AI Analysis — Live valuation */}
            <AIValuation propertyId={property.id} />

            {/* Location Intelligence */}
            <LocationIntelligence propertyId={property.id} />

            {/* Investment Potential */}
            <InvestmentPotential propertyId={property.id} />

            {/* Metadata */}
            <div className={styles.meta}>
              {property.listed_at && (
                <span className={styles.metaItem}>Listed {formatDate(property.listed_at)}</span>
              )}
              <span className={styles.metaItem}>Source: {property.data_source}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function SpecItem({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.specItem}>
      <span className={styles.specLabel}>{label}</span>
      <span className={styles.specValue}>{value}</span>
    </div>
  );
}

interface PropertyValuation {
  predicted_value: number;
  confidence_low: number;
  confidence_high: number;
  confidence_score: number;
  pricing_classification: string;
  price_gap_pct: number;
  shap_values: Record<string, number>;
}

function AIValuation({ propertyId }: { propertyId: string }) {
  const [valuation, setValuation] = useState<PropertyValuation | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<PropertyValuation>(`/valuations/${propertyId}`)
      .then(setValuation)
      .catch(() => { })
      .finally(() => setLoading(false));
  }, [propertyId]);

  if (loading) {
    return (
      <div className={styles.aiSection}>
        <h2 className={styles.sectionTitle}>🤖 AI Analysis</h2>
        <div className={`skeleton ${styles.aiSkeleton}`} />
      </div>
    );
  }

  if (!valuation) {
    return (
      <div className={styles.aiSection}>
        <h2 className={styles.sectionTitle}>🤖 AI Analysis</h2>
        <div className={styles.aiPlaceholder}>
          <p>AI valuation unavailable for this property.</p>
        </div>
      </div>
    );
  }

  const badgeClass =
    valuation.pricing_classification === 'underpriced'
      ? 'badge-underpriced'
      : valuation.pricing_classification === 'overpriced'
        ? 'badge-overpriced'
        : 'badge-fair';

  const shapEntries = Object.entries(valuation.shap_values)
    .filter(([, v]) => Math.abs(v) > 0)
    .sort(([, a], [, b]) => Math.abs(b) - Math.abs(a))
    .slice(0, 6);

  const maxShap = Math.max(...shapEntries.map(([, v]) => Math.abs(v)), 1);

  return (
    <div className={styles.aiSection}>
      <h2 className={styles.sectionTitle}>🤖 AI Valuation</h2>

      <div className={styles.valuationCard}>
        <div className={styles.valuationRow}>
          <div>
            <span className={styles.valuationLabel}>AI Predicted Value</span>
            <span className={styles.valuationPrice}>{formatINR(valuation.predicted_value)}</span>
            <span className={styles.valuationRange}>
              {formatINR(valuation.confidence_low)} — {formatINR(valuation.confidence_high)}
            </span>
          </div>
          <div className={styles.valuationRight}>
            <span className={`badge ${badgeClass} ${styles.pricingBadge}`}>
              {valuation.pricing_classification === 'underpriced'
                ? '▼ Underpriced'
                : valuation.pricing_classification === 'overpriced'
                  ? '▲ Overpriced'
                  : '● Fair Price'}
            </span>
            <span className={styles.gapPct}>
              {valuation.price_gap_pct > 0 ? '+' : ''}
              {valuation.price_gap_pct.toFixed(1)}% vs predicted
            </span>
          </div>
        </div>

        {/* Feature contributions (SHAP-like) */}
        <div className={styles.shapSection}>
          <h3 className={styles.shapTitle}>What drives this valuation</h3>
          {shapEntries.map(([feature, value]) => (
            <div key={feature} className={styles.shapRow}>
              <span className={styles.shapFeature}>
                {feature.replace(/_/g, ' ')}
              </span>
              <div className={styles.shapBarWrapper}>
                <div
                  className={`${styles.shapBar} ${value > 0 ? styles.shapPositive : styles.shapNegative}`}
                  style={{ width: `${(Math.abs(value) / maxShap) * 100}%` }}
                />
              </div>
              <span className={styles.shapValue}>
                {value > 0 ? '+' : ''}
                {formatINR(Math.abs(value))}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ── Location Intelligence Section ────────────────────────────────────────── */

interface POIItem {
  name: string;
  category: string;
  distance_meters: number;
  distance_km: number;
  travel_time_minutes_walk: number;
  travel_time_minutes_drive: number;
}

interface LocationData {
  property_id: string;
  composite_score: number;
  rating_label: string;
  sub_scores: {
    transit: number;
    schools: number;
    healthcare: number;
    shopping: number;
    parks: number;
    dining: number;
  };
  nearest_metro: POIItem | null;
  nearest_hospital: POIItem | null;
  nearest_school: POIItem | null;
  nearby_pois: POIItem[];
  location_summary: string;
}

function LocationIntelligence({ propertyId }: { propertyId: string }) {
  const [data, setData] = useState<LocationData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<LocationData>(`/location/${propertyId}`)
      .then(setData)
      .catch(() => { })
      .finally(() => setLoading(false));
  }, [propertyId]);

  if (loading) {
    return (
      <div className={styles.locationSection}>
        <h2 className={styles.sectionTitle}>📍 Location Intelligence</h2>
        <div className={`skeleton ${styles.aiSkeleton}`} />
      </div>
    );
  }

  if (!data) {
    return (
      <div className={styles.locationSection}>
        <h2 className={styles.sectionTitle}>📍 Location Intelligence</h2>
        <div className={styles.aiPlaceholder}>
          <p>Location data unavailable for this property.</p>
        </div>
      </div>
    );
  }

  const categories = [
    { key: 'transit', label: 'Transit', icon: '🚇', value: data.sub_scores.transit },
    { key: 'schools', label: 'Schools', icon: '🏫', value: data.sub_scores.schools },
    { key: 'healthcare', label: 'Healthcare', icon: '🏥', value: data.sub_scores.healthcare },
    { key: 'shopping', label: 'Shopping', icon: '🛒', value: data.sub_scores.shopping },
    { key: 'parks', label: 'Parks', icon: '🌳', value: data.sub_scores.parks },
    { key: 'dining', label: 'Dining', icon: '🍽️', value: data.sub_scores.dining },
  ];

  const scoreColor =
    data.composite_score >= 80 ? 'var(--color-primary-400)' :
      data.composite_score >= 60 ? 'var(--color-info)' :
        data.composite_score >= 40 ? 'var(--color-warning)' : 'var(--color-danger)';

  return (
    <div className={styles.locationSection}>
      <h2 className={styles.sectionTitle}>📍 Location Intelligence</h2>
      <div className={styles.locationCard}>
        {/* Composite score gauge */}
        <div className={styles.gaugeRow}>
          <div className={styles.gauge}>
            <svg viewBox="0 0 120 120" className={styles.gaugeSvg}>
              <circle cx="60" cy="60" r="50" fill="none" stroke="var(--border-color)" strokeWidth="8" />
              <circle
                cx="60" cy="60" r="50" fill="none"
                stroke={scoreColor}
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={`${(data.composite_score / 100) * 314} 314`}
                transform="rotate(-90 60 60)"
                style={{ transition: 'stroke-dasharray 1s ease' }}
              />
              <text x="60" y="55" textAnchor="middle" className={styles.gaugeScore}>
                {data.composite_score}
              </text>
              <text x="60" y="72" textAnchor="middle" className={styles.gaugeLabel}>
                {data.rating_label}
              </text>
            </svg>
          </div>
          <div className={styles.subscoreList}>
            {categories.map((cat) => (
              <div key={cat.key} className={styles.subscoreRow}>
                <span className={styles.subscoreIcon}>{cat.icon}</span>
                <span className={styles.subscoreName}>{cat.label}</span>
                <div className={styles.subscoreTrack}>
                  <div
                    className={styles.subscoreFill}
                    style={{ width: `${cat.value}%` }}
                  />
                </div>
                <span className={styles.subscoreValue}>{cat.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Nearest POIs */}
        <div className={styles.poiGrid}>
          {data.nearest_metro && (
            <div className={styles.poiCard}>
              <span className={styles.poiIcon}>🚇</span>
              <div>
                <span className={styles.poiName}>{data.nearest_metro.name}</span>
                <span className={styles.poiDistance}>
                  {data.nearest_metro.distance_km.toFixed(1)} km · {data.nearest_metro.travel_time_minutes_walk} min walk
                </span>
              </div>
            </div>
          )}
          {data.nearest_hospital && (
            <div className={styles.poiCard}>
              <span className={styles.poiIcon}>🏥</span>
              <div>
                <span className={styles.poiName}>{data.nearest_hospital.name}</span>
                <span className={styles.poiDistance}>
                  {data.nearest_hospital.distance_km.toFixed(1)} km · {data.nearest_hospital.travel_time_minutes_drive} min drive
                </span>
              </div>
            </div>
          )}
          {data.nearest_school && (
            <div className={styles.poiCard}>
              <span className={styles.poiIcon}>🏫</span>
              <div>
                <span className={styles.poiName}>{data.nearest_school.name}</span>
                <span className={styles.poiDistance}>
                  {data.nearest_school.distance_km.toFixed(1)} km · {data.nearest_school.travel_time_minutes_walk} min walk
                </span>
              </div>
            </div>
          )}
        </div>

        <p className={styles.locationSummaryText}>{data.location_summary}</p>
      </div>
    </div>
  );
}

/* ── Investment Potential Section ──────────────────────────────────────────── */

interface YearlyProjection {
  year: number;
  projected_value: number;
  cumulative_gain_pct: number;
  projected_rental_income: number;
}

interface InvestmentData {
  property_id: string;
  investment_score: number;
  investment_grade: string;
  estimated_monthly_rent: number;
  estimated_annual_rent: number;
  gross_rental_yield_pct: number;
  delhi_ncr_average_yield_pct: number;
  locality_historical_cagr_pct: number;
  projected_5yr_appreciation_pct: number;
  projected_5yr_value: number;
  infrastructure_score: number;
  demand_supply_ratio: string;
  growth_catalysts: string[];
  investment_risks: string[];
  projections: YearlyProjection[];
  summary_verdict: string;
}

function InvestmentPotential({ propertyId }: { propertyId: string }) {
  const [data, setData] = useState<InvestmentData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<InvestmentData>(`/investment/${propertyId}`)
      .then(setData)
      .catch(() => { })
      .finally(() => setLoading(false));
  }, [propertyId]);

  if (loading) {
    return (
      <div className={styles.investmentSection}>
        <h2 className={styles.sectionTitle}>📈 Investment Potential</h2>
        <div className={`skeleton ${styles.aiSkeleton}`} />
      </div>
    );
  }

  if (!data) {
    return (
      <div className={styles.investmentSection}>
        <h2 className={styles.sectionTitle}>📈 Investment Potential</h2>
        <div className={styles.aiPlaceholder}>
          <p>Investment data unavailable for this property.</p>
        </div>
      </div>
    );
  }

  const gradeColor =
    data.investment_grade === 'High Potential' ? 'var(--color-primary-400)' :
      data.investment_grade === 'Strong' ? 'var(--color-success)' :
        data.investment_grade === 'Moderate' ? 'var(--color-warning)' : 'var(--color-danger)';

  return (
    <div className={styles.investmentSection}>
      <h2 className={styles.sectionTitle}>📈 Investment Potential</h2>
      <div className={styles.investmentCard}>
        {/* Investment grade */}
        <div className={styles.investGradeRow}>
          <div className={styles.investGrade} style={{ borderColor: gradeColor }}>
            <span className={styles.investGradeScore}>{data.investment_score}</span>
            <span className={styles.investGradeLabel} style={{ color: gradeColor }}>
              {data.investment_grade}
            </span>
          </div>
          <div className={styles.investMetrics}>
            <div className={styles.investMetric}>
              <span className={styles.investMetricValue}>
                {data.gross_rental_yield_pct.toFixed(1)}%
              </span>
              <span className={styles.investMetricLabel}>Rental Yield</span>
              <span className={styles.investMetricSub}>
                vs {data.delhi_ncr_average_yield_pct}% avg
              </span>
            </div>
            <div className={styles.investMetric}>
              <span className={styles.investMetricValue}>
                {formatPercent(data.locality_historical_cagr_pct)}
              </span>
              <span className={styles.investMetricLabel}>3-yr CAGR</span>
            </div>
            <div className={styles.investMetric}>
              <span className={styles.investMetricValue}>
                {data.infrastructure_score}/100
              </span>
              <span className={styles.investMetricLabel}>Infrastructure</span>
            </div>
          </div>
        </div>

        {/* Growth catalysts & risks */}
        <div className={styles.catalystSection}>
          {data.growth_catalysts.length > 0 && (
            <div className={styles.catalystGroup}>
              <span className={styles.catalystGroupLabel}>Growth Catalysts</span>
              <div className={styles.catalystPills}>
                {data.growth_catalysts.map((c, i) => (
                  <span key={i} className={styles.catalystPill}>🚀 {c}</span>
                ))}
              </div>
            </div>
          )}
          {data.investment_risks.length > 0 && (
            <div className={styles.catalystGroup}>
              <span className={styles.catalystGroupLabel}>Risks</span>
              <div className={styles.catalystPills}>
                {data.investment_risks.map((r, i) => (
                  <span key={i} className={styles.riskPill}>⚠️ {r}</span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* 5-year projection table */}
        {data.projections.length > 0 && (
          <div className={styles.projectionSection}>
            <h3 className={styles.projectionTitle}>5-Year Capital Appreciation Projection</h3>
            <div className={styles.projectionTable}>
              <div className={styles.projectionHeader}>
                <span>Year</span>
                <span>Projected Value</span>
                <span>Gain</span>
                <span>Rental Income</span>
              </div>
              {data.projections.map((proj) => (
                <div key={proj.year} className={styles.projectionRow}>
                  <span className={styles.projYear}>{proj.year}</span>
                  <span className={styles.projValue}>{formatINR(proj.projected_value)}</span>
                  <span className={styles.projGain}>{formatPercent(proj.cumulative_gain_pct)}</span>
                  <span className={styles.projRental}>{formatINR(proj.projected_rental_income)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <p className={styles.verdictText}>{data.summary_verdict}</p>
      </div>
    </div>
  );
}

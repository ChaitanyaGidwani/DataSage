'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import { formatINR, formatArea, formatPropertyType, formatDate } from '@/lib/formatters';
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

interface ValuationData {
  predicted_value: number;
  confidence_low: number;
  confidence_high: number;
  confidence_score: number;
  pricing_classification: string;
  price_gap_pct: number;
  shap_values: Record<string, number>;
}

function AIValuation({ propertyId }: { propertyId: string }) {
  const [valuation, setValuation] = useState<ValuationData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<ValuationData>(`/valuations/${propertyId}`)
      .then(setValuation)
      .catch(() => {})
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

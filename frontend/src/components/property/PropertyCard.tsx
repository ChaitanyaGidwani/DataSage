import Link from 'next/link';
import { formatINR, formatArea, formatPropertyType } from '@/lib/formatters';
import { useCompare } from '@/contexts/CompareContext';
import styles from './PropertyCard.module.css';

interface PropertyCardProps {
  id: string;
  title: string;
  propertyType: string;
  bhk: number;
  areaSqft: number;
  listingPrice: number;
  locality: string;
  city: string;
  imageUrl?: string | null;
  pricingClassification?: string | null;
  locationScore?: number | null;
}

export default function PropertyCard({
  id,
  title,
  propertyType,
  bhk,
  areaSqft,
  listingPrice,
  locality,
  city,
  imageUrl,
  pricingClassification,
  locationScore,
}: PropertyCardProps) {
  const pricePerSqft = Math.round(listingPrice / areaSqft);
  const { addToCompare, removeFromCompare, isInCompare, isFull } = useCompare();
  const inCompare = isInCompare(id);

  const handleCompareClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (inCompare) {
      removeFromCompare(id);
    } else if (!isFull) {
      addToCompare(id);
    }
  };

  return (
    <Link href={`/properties/${id}`} className={styles.card}>
      <div className={styles.imageWrapper}>
        <div className={styles.imagePlaceholder}>
          <span className={styles.imageIcon}>🏠</span>
        </div>
        {pricingClassification && (
          <span className={`badge badge-${pricingClassification} ${styles.pricingBadge}`}>
            {pricingClassification === 'underpriced' ? '▼ Underpriced' :
             pricingClassification === 'overpriced' ? '▲ Overpriced' : '● Fair Price'}
          </span>
        )}
        <button
          className={`${styles.compareBtn} ${inCompare ? styles.compareBtnActive : ''}`}
          onClick={handleCompareClick}
          title={inCompare ? 'Remove from compare' : isFull ? 'Compare list full' : 'Add to compare'}
          aria-label={inCompare ? 'Remove from compare' : 'Add to compare'}
        >
          ⚡
        </button>
      </div>

      <div className={styles.content}>
        <div className={styles.price}>{formatINR(listingPrice)}</div>
        <div className={styles.pricePerSqft}>₹{pricePerSqft.toLocaleString('en-IN')}/sq ft</div>

        <h3 className={styles.title}>{title}</h3>

        <div className={styles.location}>
          <span className={styles.locationIcon}>📍</span>
          {locality}, {city}
        </div>

        <div className={styles.specs}>
          <span className={styles.spec}>{bhk} BHK</span>
          <span className={styles.specDot}>·</span>
          <span className={styles.spec}>{formatArea(areaSqft)}</span>
          <span className={styles.specDot}>·</span>
          <span className={styles.spec}>{formatPropertyType(propertyType)}</span>
        </div>

        {locationScore != null && (
          <div className={styles.scoreBar}>
            <span className={styles.scoreLabel}>Location</span>
            <div className={styles.scoreTrack}>
              <div className={styles.scoreFill} style={{ width: `${locationScore}%` }} />
            </div>
            <span className={styles.scoreValue}>{locationScore.toFixed(0)}</span>
          </div>
        )}
      </div>
    </Link>
  );
}


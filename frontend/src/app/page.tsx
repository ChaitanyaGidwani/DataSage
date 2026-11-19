'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Icon, IconName } from '@/components/ui/Icon';
import styles from './page.module.css';

export default function Home() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedBhk, setSelectedBhk] = useState('');
  const [selectedCity, setSelectedCity] = useState('');
  const [selectedType, setSelectedType] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (searchQuery.trim()) params.set('q', searchQuery.trim());
    if (selectedBhk) params.set('bhk', selectedBhk);
    if (selectedCity) params.set('city_id', selectedCity);
    if (selectedType) params.set('property_type', selectedType);
    router.push(`/properties?${params.toString()}`);
  };

  return (
    <>
      {/* Hero Section */}
      <section className={styles.hero}>
        <div className={styles.heroGlow} />
        <div className={styles.heroContent}>
          <div className={styles.badge}>
            <span className={styles.badgeDot} />
            Institutional Real Estate Intelligence
          </div>
          <h1 className={styles.heroTitle}>
            The AI Behind <span className="gradient-text">Better Buys</span>
          </h1>
          <p className={styles.heroSubtitle}>
            Stop guessing. DataSage analyzes property valuations, location quality,
            and micro-market trends across 4,500+ verified Delhi-NCR listings.
          </p>

          <div className={styles.heroCta}>
            <Link href="/properties" className="btn btn-primary btn-lg">
              Explore All Properties
            </Link>
            <Link href="/compare" className="btn btn-secondary btn-lg" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
              <Icon name="scale" size={18} /> Comparison Matrix
            </Link>
          </div>

          {/* Interactive Hero Search Engine */}
          <div className={styles.heroSearchCard}>
            <form onSubmit={handleSearch} className={styles.searchForm}>
              <div className={styles.searchPrimaryRow}>
                <div className={styles.searchInputWrapper}>
                  <span className={styles.searchIcon}>
                    <Icon name="search" size={18} />
                  </span>
                  <input
                    type="text"
                    className={styles.searchInput}
                    placeholder="Search by society, locality, or project (e.g., Shipra Suncity, DLF Phase 2, Tata Primanti)..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
                <button type="submit" className={`btn btn-primary ${styles.searchSubmitBtn}`}>
                  <Icon name="search" size={16} /> Search Properties
                </button>
              </div>

              <div className={styles.searchFiltersRow}>
                <select
                  className={styles.searchSelect}
                  value={selectedCity}
                  onChange={(e) => setSelectedCity(e.target.value)}
                  aria-label="Filter by City"
                >
                  <option value="">All NCR Cities</option>
                  <option value="2">Gurgaon</option>
                  <option value="3">New Delhi</option>
                  <option value="4">Ghaziabad (Indirapuram)</option>
                  <option value="1">Noida</option>
                  <option value="5">Greater Noida</option>
                  <option value="6">Faridabad</option>
                </select>

                <select
                  className={styles.searchSelect}
                  value={selectedBhk}
                  onChange={(e) => setSelectedBhk(e.target.value)}
                  aria-label="Filter by BHK"
                >
                  <option value="">All Configurations (BHK)</option>
                  <option value="1">1 BHK</option>
                  <option value="2">2 BHK</option>
                  <option value="3">3 BHK</option>
                  <option value="4">4 BHK</option>
                  <option value="5">5+ BHK</option>
                </select>

                <select
                  className={styles.searchSelect}
                  value={selectedType}
                  onChange={(e) => setSelectedType(e.target.value)}
                  aria-label="Filter by Property Type"
                >
                  <option value="">All Property Types</option>
                  <option value="apartment">Apartment / High-rise</option>
                  <option value="builder_floor">Independent Builder Floor</option>
                  <option value="house">Independent House / Villa</option>
                  <option value="plot">Residential Plot</option>
                </select>
              </div>
            </form>

            {/* Quick Search Chips */}
            <div className={styles.quickChips}>
              <span className={styles.chipLabel}>Trending:</span>
              <button
                type="button"
                className={`${styles.chipBtn} ${styles.chipHighlight}`}
                onClick={() => router.push('/properties?q=Shipra')}
              >
                Shipra Suncity
              </button>
              <button
                type="button"
                className={styles.chipBtn}
                onClick={() => router.push('/properties?q=Tata+Primanti')}
              >
                Tata Primanti
              </button>
              <button
                type="button"
                className={styles.chipBtn}
                onClick={() => router.push('/properties?q=DLF+Phase+2')}
              >
                DLF Phase 2
              </button>
              <button
                type="button"
                className={styles.chipBtn}
                onClick={() => router.push('/properties?q=Godrej')}
              >
                Godrej Nature Plus
              </button>
              <button
                type="button"
                className={styles.chipBtn}
                onClick={() => router.push('/properties?q=Suncity')}
              >
                Suncity Heights
              </button>
              <button
                type="button"
                className={`${styles.chipBtn} ${styles.chipHighlight}`}
                onClick={() => router.push('/properties?pricing_classification=underpriced')}
              >
                Underpriced Deals
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className={`section ${styles.features}`}>
        <div className="container">
          <h2 className={styles.sectionTitle}>
            What makes DataSage <span className="gradient-text">different</span>
          </h2>
          <div className={styles.featureGrid}>
            <FeatureCard
              icon="chart"
              title="AI Valuation"
              description="Statistical and machine learning models predict fair market value and classify properties as overpriced, fair, or underpriced."
            />
            <FeatureCard
              icon="map"
              title="Location Intelligence"
              description="Automated scoring based on nearby schools, hospitals, metro stations, parks, and shopping corridors."
            />
            <FeatureCard
              icon="search"
              title="Explainable Valuation"
              description="SHAP-powered contribution analysis reveals exact rupee impact of area, BHK, floor level, and locality base rates."
            />
            <FeatureCard
              icon="lightbulb"
              title="Smart Recommendations"
              description="Personalized property matches based on your budget, lifestyle priorities, and commute preferences."
            />
            <FeatureCard
              icon="scale"
              title="Side-by-Side Comparison"
              description="Compare up to 4 properties across 15+ dimensions with automated best-pick and trade-off analysis."
            />
            <FeatureCard
              icon="trendingUp"
              title="Investment Insights"
              description="Locality price trends, rental yield estimates, and 5-year capital appreciation projections for investors."
            />
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className={styles.stats}>
        <div className="container">
          <div className={styles.statsGrid}>
            <StatCard number="4,557" label="Verified NCR Listings" />
            <StatCard number="50+" label="Delhi-NCR Localities" />
            <StatCard number="87.9%" label="ML Model R² Accuracy" />
            <StatCard number="6" label="NCR Cities Covered" />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className={styles.cta}>
        <div className="container">
          <div className={styles.ctaCard}>
            <h2 className={styles.ctaTitle}>Ready to make smarter property decisions?</h2>
            <p className={styles.ctaText}>
              Explore explainable AI valuations, location intelligence, and multi-asset comparison matrices.
            </p>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
              <Link href="/properties" className="btn btn-primary btn-lg">
                Start Searching
              </Link>
              <Link href="/compare?ids=a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d,f24cd120-abaa-43da-9395-1edde18da205,7cb1a4ec-b076-49be-b01a-909a7af33fd3" className="btn btn-secondary btn-lg">
                View Sample Comparison
              </Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: IconName;
  title: string;
  description: string;
}) {
  return (
    <div className={styles.featureCard}>
      <span className={styles.featureIcon}>
        <Icon name={icon} size={22} />
      </span>
      <h3 className={styles.featureTitle}>{title}</h3>
      <p className={styles.featureDesc}>{description}</p>
    </div>
  );
}

function StatCard({ number, label }: { number: string; label: string }) {
  return (
    <div className={styles.statCard}>
      <span className={styles.statNumber}>{number}</span>
      <span className={styles.statLabel}>{label}</span>
    </div>
  );
}

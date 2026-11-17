import Link from 'next/link';
import { Icon, IconName } from '@/components/ui/Icon';
import styles from './page.module.css';

export default function Home() {
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
            and micro-market trends to help you make smarter residential investments across Delhi-NCR.
          </p>
          <div className={styles.heroCta}>
            <Link href="/properties" className="btn btn-primary btn-lg">
              Explore Properties
            </Link>
            <Link href="/register" className="btn btn-secondary btn-lg">
              Create Free Account
            </Link>
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
            <StatCard number="4,500+" label="Verified Listings" />
            <StatCard number="50+" label="Delhi-NCR Localities" />
            <StatCard number="30+" label="Valuation Features" />
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
              Create an account to unlock explainable AI valuations, personalized recommendations,
              and side-by-side comparison matrices.
            </p>
            <Link href="/register" className="btn btn-primary btn-lg">
              Get Started — Free Access
            </Link>
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

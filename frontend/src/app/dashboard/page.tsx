'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';
import { formatDate } from '@/lib/formatters';
import { Icon } from '@/components/ui/Icon';
import styles from './page.module.css';

interface SavedPropertyItem {
  id: string;
  property_id: string;
  notes: string | null;
  created_at: string;
}

interface SearchHistoryItem {
  id: string;
  search_params: Record<string, unknown>;
  result_count: number;
  created_at: string;
}

export default function DashboardPage() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  const [savedProperties, setSavedProperties] = useState<SavedPropertyItem[]>([]);
  const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated) {
      Promise.all([
        api.get<SavedPropertyItem[]>('/saved-properties').catch(() => []),
        api.get<SearchHistoryItem[]>('/search-history').catch(() => []),
      ])
        .then(([saved, history]) => {
          setSavedProperties(saved);
          setSearchHistory(history);
        })
        .finally(() => setLoading(false));
    }
  }, [isAuthenticated]);

  if (isLoading || !isAuthenticated || loading) {
    return (
      <div className={styles.page}>
        <div className="container">
          <div className="skeleton" style={{ height: 300 }} />
        </div>
      </div>
    );
  }

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
              <span className={styles.statNumber}>{savedProperties.length}</span>
              <span className={styles.statLabel}>Saved Listings</span>
            </div>
          </div>
          <div className={styles.statCard}>
            <span className={styles.statIcon} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Icon name="search" size={20} />
            </span>
            <div>
              <span className={styles.statNumber}>{searchHistory.length}</span>
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

        <div className={styles.grid}>
          {/* Saved Properties */}
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>Saved Properties</h2>
            {savedProperties.length === 0 ? (
              <div className={styles.empty}>
                <p>No saved properties yet. Browse and track properties of interest.</p>
                <Link href="/properties" className="btn btn-primary btn-sm">
                  Browse Properties
                </Link>
              </div>
            ) : (
              <div className={styles.list}>
                {savedProperties.map((item) => (
                  <Link
                    key={item.id}
                    href={`/properties/${item.property_id}`}
                    className={styles.listItem}
                  >
                    <span className={styles.listIcon} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Icon name="building" size={18} />
                    </span>
                    <div>
                      <span className={styles.listTitle}>Property Analysis</span>
                      <span className={styles.listMeta}>Saved {formatDate(item.created_at)}</span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </section>

          {/* Search History */}
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>Recent Searches</h2>
            {searchHistory.length === 0 ? (
              <div className={styles.empty}>
                <p>No search history yet. Explore Delhi-NCR micro-markets.</p>
                <Link href="/properties" className="btn btn-primary btn-sm">
                  Start Exploring
                </Link>
              </div>
            ) : (
              <div className={styles.list}>
                {searchHistory.map((item) => (
                  <div key={item.id} className={styles.listItem}>
                    <span className={styles.listIcon} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Icon name="search" size={18} />
                    </span>
                    <div>
                      <span className={styles.listTitle}>
                        {item.result_count} listings found
                      </span>
                      <span className={styles.listMeta}>{formatDate(item.created_at)}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>

        {/* Quick actions */}
        <div className={styles.actions}>
          <Link href="/properties" className="btn btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
            <Icon name="search" size={16} /> Search Properties
          </Link>
          <Link href="/properties" className="btn btn-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
            <Icon name="chart" size={16} /> Market Analytics
          </Link>
        </div>
      </div>
    </div>
  );
}

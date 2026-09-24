'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';
import styles from './page.module.css';

interface AdminStats {
  total_properties: number;
  total_valuations: number;
  total_localities: number;
  active_users: number;
  health_status: string;
  model_version: string;
}

export default function AdminPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated) {
      api
        .get<AdminStats>('/admin/stats')
        .then(setStats)
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [isAuthenticated]);

  const handleTriggerValuations = async () => {
    setTriggering(true);
    setToast(null);
    try {
      const result = await api.post<{ message: string; valuations_created: number }>(
        '/admin/trigger-valuations'
      );
      setToast({
        type: 'success',
        message: `${result.valuations_created} valuations created successfully.`,
      });
      // Refresh stats
      const refreshed = await api.get<AdminStats>('/admin/stats');
      setStats(refreshed);
    } catch {
      setToast({ type: 'error', message: 'Failed to trigger valuations. Check server logs.' });
    } finally {
      setTriggering(false);
    }
  };

  if (isLoading || !isAuthenticated) {
    return (
      <div className={styles.page}>
        <div className="container">
          <div className="skeleton" style={{ height: 400 }} />
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className="container">
        <div className={styles.header}>
          <h1 className={styles.title}>
            Admin <span className="gradient-text">Dashboard</span>
          </h1>
          <p className={styles.subtitle}>System overview and operations panel</p>
        </div>

        {/* Metrics grid */}
        {loading ? (
          <div className={styles.metricsGrid}>
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className={`skeleton ${styles.skeleton}`} />
            ))}
          </div>
        ) : stats ? (
          <div className={styles.metricsGrid}>
            <div className={styles.metricCard}>
              <div className={styles.metricIcon}>🏠</div>
              <div className={styles.metricInfo}>
                <span className={styles.metricValue}>
                  {stats.total_properties.toLocaleString()}
                </span>
                <span className={styles.metricLabel}>Total Properties</span>
              </div>
            </div>

            <div className={styles.metricCard}>
              <div className={styles.metricIcon}>🤖</div>
              <div className={styles.metricInfo}>
                <span className={styles.metricValue}>
                  {stats.total_valuations.toLocaleString()}
                </span>
                <span className={styles.metricLabel}>Total Valuations</span>
              </div>
            </div>

            <div className={styles.metricCard}>
              <div className={styles.metricIcon}>📍</div>
              <div className={styles.metricInfo}>
                <span className={styles.metricValue}>{stats.total_localities}</span>
                <span className={styles.metricLabel}>Active Localities</span>
              </div>
            </div>

            <div className={styles.metricCard}>
              <div className={styles.metricIcon}>👥</div>
              <div className={styles.metricInfo}>
                <span className={styles.metricValue}>{stats.active_users}</span>
                <span className={styles.metricLabel}>Active Users</span>
              </div>
            </div>

            <div className={styles.metricCard}>
              <div className={styles.metricIcon}>💚</div>
              <div className={styles.metricInfo}>
                <span
                  className={`${styles.healthBadge} ${
                    stats.health_status === 'healthy' ? styles.healthOk : styles.healthError
                  }`}
                >
                  ● {stats.health_status || 'OK'}
                </span>
                <span className={styles.metricLabel}>System Health</span>
              </div>
            </div>
          </div>
        ) : null}

        {/* Operations */}
        <div className={styles.actionsSection}>
          <h2 className={styles.actionsTitle}>Operations</h2>
          <p className={styles.actionsDescription}>
            Trigger bulk actions for the platform. Valuations will be generated for all properties
            that don&apos;t have one yet.
          </p>

          <div className={styles.actionRow}>
            <button
              onClick={handleTriggerValuations}
              className="btn btn-primary btn-lg"
              disabled={triggering}
            >
              {triggering ? '⏳ Running...' : '🚀 Trigger Bulk Valuations'}
            </button>

            {stats?.model_version && (
              <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)' }}>
                Active Model: {stats.model_version}
              </span>
            )}
          </div>

          {toast && (
            <div
              className={`${styles.toast} ${
                toast.type === 'success' ? styles.toastSuccess : styles.toastError
              }`}
            >
              {toast.type === 'success' ? '✅' : '❌'} {toast.message}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

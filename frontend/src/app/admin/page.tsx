'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';
import { Icon } from '@/components/ui/Icon';
import styles from './page.module.css';

interface AdminStats {
  total_properties: number;
  total_valuations: number;
  total_localities: number;
  active_users: number;
  health_status: string;
  model_version: string;
}

interface DatasetImportInfo {
  file_name: string;
  total_rows: number;
  valid_rows: number;
  quarantined_rows: number;
  status: string;
  completed_at: string | null;
}

interface DatasetInfo {
  id: string;
  name: string;
  status: string;
  description: string;
  property_count: number;
  imports: DatasetImportInfo[];
}

export default function AdminPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  const [stats, setStats] = useState<AdminStats | null>(null);
  const [datasets, setDatasets] = useState<DatasetInfo[]>([]);
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
      Promise.all([
        api.get<AdminStats>('/admin/stats').then(setStats),
        api
          .get<any>('/admin/datasets')
          .then((res) => setDatasets(Array.isArray(res) ? res : res?.data || []))
          .catch(() => setDatasets([])),
      ])
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [isAuthenticated]);

  const handleTriggerValuations = async () => {
    setTriggering(true);
    setToast(null);
    try {
      const result = await api.post<{ message?: string; valuations_created?: number; valuations_generated?: number }>(
        '/admin/trigger-valuations'
      );
      const count = result.valuations_created ?? result.valuations_generated ?? 0;
      setToast({
        type: 'success',
        message: `${count} valuations verified and updated successfully.`,
      });
      // Refresh stats
      const refreshed = await api.get<AdminStats>('/admin/stats');
      setStats(refreshed);
    } catch {
      setToast({ type: 'error', message: 'Failed to trigger valuations. Check server connection.' });
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
            Admin <span className="gradient-text">Command Center</span>
          </h1>
          <p className={styles.subtitle}>
            Platform telemetry, ingestion pipelines, and machine learning operations
          </p>
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
              <div className={styles.metricIcon}>
                <Icon name="building" size={24} />
              </div>
              <div className={styles.metricInfo}>
                <span className={styles.metricValue}>
                  {stats.total_properties.toLocaleString()}
                </span>
                <span className={styles.metricLabel}>Total Properties</span>
              </div>
            </div>

            <div className={styles.metricCard}>
              <div className={styles.metricIcon}>
                <Icon name="sparkles" size={24} />
              </div>
              <div className={styles.metricInfo}>
                <span className={styles.metricValue}>
                  {stats.total_valuations.toLocaleString()}
                </span>
                <span className={styles.metricLabel}>Total Valuations</span>
              </div>
            </div>

            <div className={styles.metricCard}>
              <div className={styles.metricIcon}>
                <Icon name="pin" size={24} />
              </div>
              <div className={styles.metricInfo}>
                <span className={styles.metricValue}>{stats.total_localities}</span>
                <span className={styles.metricLabel}>Active Localities</span>
              </div>
            </div>

            <div className={styles.metricCard}>
              <div className={styles.metricIcon}>
                <Icon name="users" size={24} />
              </div>
              <div className={styles.metricInfo}>
                <span className={styles.metricValue}>{stats.active_users}</span>
                <span className={styles.metricLabel}>Active Accounts</span>
              </div>
            </div>

            <div className={styles.metricCard}>
              <div className={styles.metricIcon}>
                <Icon name="pulse" size={24} />
              </div>
              <div className={styles.metricInfo}>
                <span
                  className={`${styles.healthBadge} ${
                    stats.health_status === 'healthy' ? styles.healthOk : styles.healthError
                  }`}
                >
                  ● {stats.health_status === 'healthy' ? 'Operational' : stats.health_status}
                </span>
                <span className={styles.metricLabel}>System Status</span>
              </div>
            </div>
          </div>
        ) : null}

        {/* Real Ingested Datasets Section */}
        {datasets.length > 0 && (
          <div className={styles.datasetSection}>
            <div className={styles.datasetHeader}>
              <div>
                <h2 className={styles.actionsTitle}>Real Data Ingestion Pipelines</h2>
                <p className={styles.actionsDescription} style={{ marginBottom: 0 }}>
                  Curated and verified external real estate corpora synchronized from GitHub repositories
                </p>
              </div>
              <span className={styles.sourceBadge}>
                <Icon name="database" size={13} /> GitHub Synchronized
              </span>
            </div>

            <div className={styles.datasetGrid}>
              {datasets.map((ds) => {
                const latestImp = ds.imports && ds.imports.length > 0 ? ds.imports[0] : null;
                return (
                  <div key={ds.id} className={styles.datasetCard}>
                    <div>
                      <div className={styles.datasetTitle}>
                        <Icon name="database" size={18} />
                        {ds.name}
                      </div>
                      <p className={styles.datasetDesc}>{ds.description}</p>
                    </div>

                    <div className={styles.datasetMeta}>
                      <span>
                        <strong>{ds.property_count.toLocaleString()}</strong> live listings
                      </span>
                      {latestImp && (
                        <span style={{ color: 'var(--text-muted)' }}>
                          File: {latestImp.file_name}
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Operations */}
        <div className={styles.actionsSection}>
          <h2 className={styles.actionsTitle}>Valuation Engine Operations</h2>
          <p className={styles.actionsDescription}>
            Evaluate feature distributions, compute SHAP attribution weights, and refresh pricing classifications.
          </p>

          <div className={styles.actionRow}>
            <button
              onClick={handleTriggerValuations}
              className="btn btn-primary btn-lg"
              disabled={triggering}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}
            >
              <Icon name={triggering ? 'clock' : 'sparkles'} size={18} />
              {triggering ? 'Computing Valuations...' : 'Refresh Valuation Pipeline'}
            </button>

            {stats?.model_version && (
              <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)' }}>
                Active Valuation Model: <strong>{stats.model_version}</strong>
              </span>
            )}
          </div>

          {toast && (
            <div
              className={`${styles.toast} ${
                toast.type === 'success' ? styles.toastSuccess : styles.toastError
              }`}
              style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
            >
              <Icon name={toast.type === 'success' ? 'check' : 'alert'} size={16} />
              {toast.message}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

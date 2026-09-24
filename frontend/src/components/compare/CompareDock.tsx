'use client';

import Link from 'next/link';
import { useCompare } from '@/contexts/CompareContext';
import styles from './CompareDock.module.css';

export default function CompareDock() {
  const { compareIds, clearCompare } = useCompare();

  const isVisible = compareIds.length > 0;

  return (
    <div className={`${styles.dock} ${isVisible ? styles.dockVisible : ''}`}>
      <div className={styles.inner}>
        <div className={styles.info}>
          <span className={styles.icon}>⚡</span>
          <div>
            <span className={styles.label}>Compare Properties</span>
            <span className={styles.count}> — {compareIds.length} of 4 selected</span>
          </div>
        </div>

        <div className={styles.dots}>
          {[0, 1, 2, 3].map((i) => (
            <div
              key={i}
              className={`${styles.dot} ${i < compareIds.length ? styles.dotFilled : ''}`}
            />
          ))}
        </div>

        <div className={styles.actions}>
          <button onClick={clearCompare} className="btn btn-ghost btn-sm">
            Clear
          </button>
          {compareIds.length >= 2 && (
            <Link
              href={`/compare?ids=${compareIds.join(',')}`}
              className="btn btn-primary btn-sm"
            >
              Compare Now →
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}

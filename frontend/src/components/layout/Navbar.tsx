'use client';

import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { useCompare } from '@/contexts/CompareContext';
import styles from './Navbar.module.css';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const { compareIds } = useCompare();

  return (
    <nav className={styles.navbar}>
      <div className={styles.inner}>
        <Link href="/" className={styles.logo}>
          <span className={styles.logoIcon}>◆</span>
          <span className={styles.logoText}>DataSage</span>
        </Link>

        <div className={styles.links}>
          <Link href="/properties" className={styles.navLink}>
            Search
          </Link>
          <Link href="/compare" className={styles.navLink}>
            Compare{compareIds.length > 0 ? ` (${compareIds.length})` : ''}
          </Link>
          {isAuthenticated && (
            <>
              <Link href="/dashboard" className={styles.navLink}>
                Dashboard
              </Link>
              <Link href="/admin" className={styles.navLink}>
                Admin
              </Link>
            </>
          )}
        </div>

        <div className={styles.actions}>
          {isAuthenticated ? (
            <div className={styles.userMenu}>
              <Link href="/onboarding" className="btn btn-ghost btn-sm">
                ✨ Preferences
              </Link>
              <span className={styles.userName}>{user?.name}</span>
              <button onClick={logout} className="btn btn-ghost btn-sm">
                Sign Out
              </button>
            </div>
          ) : (
            <div className={styles.authButtons}>
              <Link href="/login" className="btn btn-ghost btn-sm">
                Sign In
              </Link>
              <Link href="/register" className="btn btn-primary btn-sm">
                Get Started
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}


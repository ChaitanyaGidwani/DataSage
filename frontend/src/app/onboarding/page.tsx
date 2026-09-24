'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';
import { formatINR } from '@/lib/formatters';
import styles from './page.module.css';

interface LocalityOption {
  id: number;
  name: string;
  city: string;
  avg_price_per_sqft: number | null;
}

const LIFESTYLE_OPTIONS = [
  { id: 'transit', label: 'Transit', icon: '🚇' },
  { id: 'schools', label: 'Schools', icon: '🏫' },
  { id: 'healthcare', label: 'Healthcare', icon: '🏥' },
  { id: 'shopping', label: 'Shopping', icon: '🛒' },
  { id: 'parks', label: 'Parks', icon: '🌳' },
  { id: 'dining', label: 'Dining', icon: '🍽️' },
  { id: 'safety', label: 'Safety', icon: '🛡️' },
  { id: 'nightlife', label: 'Nightlife', icon: '🌙' },
];

const PROPERTY_TYPES = [
  { id: 'apartment', label: 'Apartment' },
  { id: 'builder_floor', label: 'Builder Floor' },
  { id: 'house', label: 'House' },
  { id: 'plot', label: 'Plot' },
];

export default function OnboardingPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  const [step, setStep] = useState(0);
  const [saving, setSaving] = useState(false);
  const [done, setDone] = useState(false);

  // Preferences state
  const [budgetMin, setBudgetMin] = useState(2000000); // 20L
  const [budgetMax, setBudgetMax] = useState(15000000); // 1.5Cr
  const [bhkPrefs, setBhkPrefs] = useState<number[]>([2, 3]);
  const [propertyTypes, setPropertyTypes] = useState<string[]>(['apartment']);
  const [selectedLocalities, setSelectedLocalities] = useState<number[]>([]);
  const [lifestylePriorities, setLifestylePriorities] = useState<string[]>(['transit', 'schools']);

  // Localities data
  const [localities, setLocalities] = useState<LocalityOption[]>([]);
  const [localitySearch, setLocalitySearch] = useState('');

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  useEffect(() => {
    api
      .get<{ data: LocalityOption[] }>('/localities')
      .then((res) => setLocalities(res.data || []))
      .catch(() => {});
  }, []);

  const totalSteps = 4;

  const toggleItem = <T,>(arr: T[], item: T): T[] =>
    arr.includes(item) ? arr.filter((i) => i !== item) : [...arr, item];

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.put('/preferences', {
        budget_min: budgetMin,
        budget_max: budgetMax,
        bhk_preferences: bhkPrefs,
        preferred_locality_ids: selectedLocalities,
        lifestyle_priorities: lifestylePriorities,
        property_type_preferences: propertyTypes,
      });
      setDone(true);
      setTimeout(() => router.push('/dashboard'), 2000);
    } catch {
      // Handle silently
    } finally {
      setSaving(false);
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

  if (done) {
    return (
      <div className={styles.page}>
        <div className="container">
          <div className={styles.successState}>
            <span className={styles.successIcon}>🎉</span>
            <h1 className={styles.successTitle}>Preferences Saved!</h1>
            <p className={styles.successText}>
              We&apos;ll use these to find your perfect property. Redirecting to dashboard...
            </p>
          </div>
        </div>
      </div>
    );
  }

  const filteredLocalities = localities.filter((loc) =>
    loc.name.toLowerCase().includes(localitySearch.toLowerCase())
  );

  return (
    <div className={styles.page}>
      <div className="container">
        <div className={styles.header}>
          <h1 className={styles.title}>
            Tell us about your <span className="gradient-text">Dream Home</span>
          </h1>
          <p className={styles.subtitle}>
            Help us personalize your experience with a few quick preferences
          </p>
        </div>

        {/* Progress bar */}
        <div className={styles.progressBar}>
          {Array.from({ length: totalSteps }).map((_, i) => (
            <div
              key={i}
              className={`${styles.progressStep} ${
                i === step ? styles.progressActive : i < step ? styles.progressDone : ''
              }`}
            />
          ))}
        </div>

        {/* Step 0: Budget */}
        {step === 0 && (
          <div className={styles.stepCard}>
            <h2 className={styles.stepTitle}>
              <span className={styles.stepIcon}>💰</span> Budget Range
            </h2>
            <p className={styles.stepDescription}>
              What&apos;s your budget range for a property in Delhi-NCR?
            </p>

            <div className={styles.budgetDisplay}>
              <div>
                <span className={styles.budgetLabel}>Minimum</span>
                <span className={styles.budgetValue}>{formatINR(budgetMin)}</span>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span className={styles.budgetLabel}>Maximum</span>
                <span className={styles.budgetValue}>{formatINR(budgetMax)}</span>
              </div>
            </div>

            <div>
              <label className="input-label">Min Budget</label>
              <input
                type="range"
                className={styles.rangeInput}
                min={1000000}
                max={50000000}
                step={500000}
                value={budgetMin}
                onChange={(e) => {
                  const val = Number(e.target.value);
                  setBudgetMin(Math.min(val, budgetMax - 500000));
                }}
              />
            </div>
            <div>
              <label className="input-label">Max Budget</label>
              <input
                type="range"
                className={styles.rangeInput}
                min={1000000}
                max={100000000}
                step={500000}
                value={budgetMax}
                onChange={(e) => {
                  const val = Number(e.target.value);
                  setBudgetMax(Math.max(val, budgetMin + 500000));
                }}
              />
            </div>
          </div>
        )}

        {/* Step 1: BHK & Property Type */}
        {step === 1 && (
          <div className={styles.stepCard}>
            <h2 className={styles.stepTitle}>
              <span className={styles.stepIcon}>🏠</span> BHK & Property Type
            </h2>
            <p className={styles.stepDescription}>Select your preferred configurations.</p>

            <label className="input-label">BHK Preference</label>
            <div className={styles.checkGrid}>
              {[1, 2, 3, 4, 5].map((bhk) => (
                <div
                  key={bhk}
                  className={`${styles.checkItem} ${bhkPrefs.includes(bhk) ? styles.checkItemActive : ''}`}
                  onClick={() => setBhkPrefs(toggleItem(bhkPrefs, bhk))}
                >
                  {bhk} BHK
                </div>
              ))}
            </div>

            <label className="input-label" style={{ marginTop: 'var(--space-4)' }}>Property Type</label>
            <div className={styles.checkGrid}>
              {PROPERTY_TYPES.map((pt) => (
                <div
                  key={pt.id}
                  className={`${styles.checkItem} ${propertyTypes.includes(pt.id) ? styles.checkItemActive : ''}`}
                  onClick={() => setPropertyTypes(toggleItem(propertyTypes, pt.id))}
                >
                  {pt.label}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Step 2: Localities */}
        {step === 2 && (
          <div className={styles.stepCard}>
            <h2 className={styles.stepTitle}>
              <span className={styles.stepIcon}>📍</span> Preferred Localities
            </h2>
            <p className={styles.stepDescription}>
              Select localities you&apos;re interested in across Delhi-NCR.
            </p>

            <div className={styles.localitySearch}>
              <input
                type="text"
                className="input"
                placeholder="Search localities..."
                value={localitySearch}
                onChange={(e) => setLocalitySearch(e.target.value)}
              />
            </div>

            <div className={styles.localityList}>
              {filteredLocalities.map((loc) => {
                const isSelected = selectedLocalities.includes(loc.id);
                return (
                  <div
                    key={loc.id}
                    className={`${styles.localityItem} ${isSelected ? styles.localityItemActive : ''}`}
                    onClick={() => setSelectedLocalities(toggleItem(selectedLocalities, loc.id))}
                  >
                    <div>
                      <span>{loc.name}</span>
                      <span className={styles.localityCity}> — {loc.city}</span>
                    </div>
                    <div className={`${styles.localityCheck} ${isSelected ? styles.localityCheckActive : ''}`}>
                      {isSelected ? '✓' : ''}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Step 3: Lifestyle Priorities */}
        {step === 3 && (
          <div className={styles.stepCard}>
            <h2 className={styles.stepTitle}>
              <span className={styles.stepIcon}>✨</span> Lifestyle Priorities
            </h2>
            <p className={styles.stepDescription}>
              What matters most to you in a neighborhood?
            </p>

            <div className={styles.chipGrid}>
              {LIFESTYLE_OPTIONS.map((opt) => (
                <div
                  key={opt.id}
                  className={`${styles.chip} ${lifestylePriorities.includes(opt.id) ? styles.chipActive : ''}`}
                  onClick={() => setLifestylePriorities(toggleItem(lifestylePriorities, opt.id))}
                >
                  <span className={styles.chipIcon}>{opt.icon}</span>
                  {opt.label}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className={styles.navRow}>
          {step > 0 ? (
            <button onClick={() => setStep(step - 1)} className="btn btn-secondary">
              ← Back
            </button>
          ) : (
            <div />
          )}
          {step < totalSteps - 1 ? (
            <button onClick={() => setStep(step + 1)} className="btn btn-primary">
              Next →
            </button>
          ) : (
            <button onClick={handleSave} className="btn btn-primary btn-lg" disabled={saving}>
              {saving ? 'Saving...' : '✨ Save Preferences'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

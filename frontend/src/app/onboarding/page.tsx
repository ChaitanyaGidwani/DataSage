'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';
import { formatINR } from '@/lib/formatters';
import { Icon, IconName } from '@/components/ui/Icon';
import styles from './page.module.css';

interface LocalityOption {
  id: number;
  name: string;
  city: string;
  avg_price_per_sqft: number | null;
}

const LIFESTYLE_OPTIONS: Array<{ id: string; label: string; icon: IconName }> = [
  { id: 'transit', label: 'Rapid Transit', icon: 'transit' },
  { id: 'schools', label: 'Top Schools', icon: 'school' },
  { id: 'healthcare', label: 'Healthcare & Hospitals', icon: 'hospital' },
  { id: 'shopping', label: 'Shopping & Retail', icon: 'shopping' },
  { id: 'parks', label: 'Parks & Green Spaces', icon: 'park' },
  { id: 'dining', label: 'Dining & Cafes', icon: 'dining' },
  { id: 'safety', label: 'Gated Security', icon: 'shield' },
  { id: 'nightlife', label: 'Nightlife & Social Hubs', icon: 'moon' },
];

const PROPERTY_TYPES = [
  { id: 'apartment', label: 'Apartment' },
  { id: 'builder_floor', label: 'Builder Floor' },
  { id: 'house', label: 'Independent House / Villa' },
  { id: 'plot', label: 'Residential Plot' },
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

  // Available localities
  const [localities, setLocalities] = useState<LocalityOption[]>([]);
  const [localitySearch, setLocalitySearch] = useState('');

  const totalSteps = 4;

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  useEffect(() => {
    api
      .get<LocalityOption[]>('/localities')
      .then(setLocalities)
      .catch(() => {});
  }, []);

  const toggleItem = <T,>(list: T[], item: T): T[] =>
    list.includes(item) ? list.filter((i) => i !== item) : [...list, item];

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.put('/preferences', {
        budget_min: budgetMin,
        budget_max: budgetMax,
        bhk_preference: bhkPrefs,
        property_types: propertyTypes,
        preferred_localities: selectedLocalities,
        lifestyle_priorities: lifestylePriorities,
      });
      setDone(true);
      setTimeout(() => router.push('/dashboard'), 1500);
    } catch {
      alert('Failed to save preferences. Please try again.');
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
            <span className={styles.successIcon} style={{ display: 'flex', justifyContent: 'center' }}>
              <Icon name="check" size={48} />
            </span>
            <h1 className={styles.successTitle}>Preferences Configured</h1>
            <p className={styles.successText}>
              Your criteria has been calibrated with DataSage AI. Redirecting to your dashboard...
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
            Buyer Profile & <span className="gradient-text">Preferences</span>
          </h1>
          <p className={styles.subtitle}>
            Calibrate your search criteria to unlock tailored valuation analysis and recommendations
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
            <h2 className={styles.stepTitle} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Icon name="wallet" size={20} /> Budget Allocation
            </h2>
            <p className={styles.stepDescription}>
              Define your target acquisition budget for properties across Delhi-NCR.
            </p>

            <div className={styles.budgetDisplay}>
              <div>
                <span className={styles.budgetLabel}>Minimum Target</span>
                <span className={styles.budgetValue}>{formatINR(budgetMin)}</span>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span className={styles.budgetLabel}>Maximum Ceiling</span>
                <span className={styles.budgetValue}>{formatINR(budgetMax)}</span>
              </div>
            </div>

            <div>
              <label className="input-label">Min Budget (INR)</label>
              <input
                type="range"
                min="1000000"
                max="50000000"
                step="500000"
                value={budgetMin}
                onChange={(e) => {
                  const val = Number(e.target.value);
                  if (val <= budgetMax) setBudgetMin(val);
                }}
                className="range-input"
                style={{ width: '100%', accentColor: 'var(--color-primary-400)' }}
              />
            </div>

            <div style={{ marginTop: 'var(--space-4)' }}>
              <label className="input-label">Max Budget (INR)</label>
              <input
                type="range"
                min="2000000"
                max="100000000"
                step="1000000"
                value={budgetMax}
                onChange={(e) => {
                  const val = Number(e.target.value);
                  if (val >= budgetMin) setBudgetMax(val);
                }}
                className="range-input"
                style={{ width: '100%', accentColor: 'var(--color-primary-400)' }}
              />
            </div>
          </div>
        )}

        {/* Step 1: BHK & Property Type */}
        {step === 1 && (
          <div className={styles.stepCard}>
            <h2 className={styles.stepTitle} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Icon name="building" size={20} /> Configuration & Typology
            </h2>
            <p className={styles.stepDescription}>Select your required layouts and preferred asset classes.</p>

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
            <h2 className={styles.stepTitle} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Icon name="pin" size={20} /> Target Localities
            </h2>
            <p className={styles.stepDescription}>
              Select specific micro-markets of interest across Delhi, Gurgaon, Noida, and NCR.
            </p>

            <div className={styles.localitySearch}>
              <input
                type="text"
                className="input"
                placeholder="Search micro-markets (e.g. Rohini, Golf Course Road, Sector 150)..."
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
                      {isSelected ? <Icon name="check" size={12} /> : null}
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
            <h2 className={styles.stepTitle} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Icon name="sliders" size={20} /> Lifestyle & Infrastructure Priorities
            </h2>
            <p className={styles.stepDescription}>
              Rank the civic amenities and infrastructure factors that matter most for your household.
            </p>

            <div className={styles.chipGrid}>
              {LIFESTYLE_OPTIONS.map((opt) => (
                <div
                  key={opt.id}
                  className={`${styles.chip} ${lifestylePriorities.includes(opt.id) ? styles.chipActive : ''}`}
                  onClick={() => setLifestylePriorities(toggleItem(lifestylePriorities, opt.id))}
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}
                >
                  <span className={styles.chipIcon} style={{ display: 'flex', alignItems: 'center' }}>
                    <Icon name={opt.icon} size={16} />
                  </span>
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
              Back
            </button>
          ) : (
            <div />
          )}
          {step < totalSteps - 1 ? (
            <button onClick={() => setStep(step + 1)} className="btn btn-primary">
              Continue
            </button>
          ) : (
            <button
              onClick={handleSave}
              className="btn btn-primary btn-lg"
              disabled={saving}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}
            >
              <Icon name="check" size={16} />
              {saving ? 'Saving...' : 'Save Preferences'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

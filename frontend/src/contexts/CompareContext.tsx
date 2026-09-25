'use client';

import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';

interface CompareContextType {
  compareIds: string[];
  addToCompare: (id: string) => void;
  removeFromCompare: (id: string) => void;
  clearCompare: () => void;
  isInCompare: (id: string) => boolean;
  isFull: boolean;
}

const CompareContext = createContext<CompareContextType | null>(null);

const MAX_COMPARE = 4;
const STORAGE_KEY = 'datasage_compare_ids';

export function CompareProvider({ children }: { children: ReactNode }) {
  const [compareIds, setCompareIds] = useState<string[]>([]);

  // Hydrate from sessionStorage on mount
  useEffect(() => {
    try {
      const stored = sessionStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed)) {
          queueMicrotask(() => {
            setCompareIds(parsed.slice(0, MAX_COMPARE));
          });
        }
      }
    } catch {
      // Ignore parse errors
    }
  }, []);

  // Persist to sessionStorage on change
  useEffect(() => {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(compareIds));
  }, [compareIds]);

  const addToCompare = useCallback((id: string) => {
    setCompareIds((prev) => {
      if (prev.includes(id) || prev.length >= MAX_COMPARE) return prev;
      return [...prev, id];
    });
  }, []);

  const removeFromCompare = useCallback((id: string) => {
    setCompareIds((prev) => prev.filter((pid) => pid !== id));
  }, []);

  const clearCompare = useCallback(() => {
    setCompareIds([]);
  }, []);

  const isInCompare = useCallback(
    (id: string) => compareIds.includes(id),
    [compareIds]
  );

  return (
    <CompareContext.Provider
      value={{
        compareIds,
        addToCompare,
        removeFromCompare,
        clearCompare,
        isInCompare,
        isFull: compareIds.length >= MAX_COMPARE,
      }}
    >
      {children}
    </CompareContext.Provider>
  );
}

export function useCompare() {
  const context = useContext(CompareContext);
  if (!context) {
    throw new Error('useCompare must be used within CompareProvider');
  }
  return context;
}

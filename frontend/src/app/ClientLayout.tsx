'use client';

import { AuthProvider } from '@/contexts/AuthContext';
import { CompareProvider } from '@/contexts/CompareContext';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import CompareDock from '@/components/compare/CompareDock';

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <CompareProvider>
        <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <Navbar />
          <main style={{ flex: 1 }}>{children}</main>
          <Footer />
          <CompareDock />
        </div>
      </CompareProvider>
    </AuthProvider>
  );
}

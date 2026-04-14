'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import type { User } from '@supabase/supabase-js';
import { supabase } from '@/lib/supabase';
import { 
  LayoutDashboard, 
  FileUp, 
  Search, 
  Bookmark, 
  Settings, 
  LogOut, 
  User as UserIcon,
} from 'lucide-react';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const checkUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        router.push('/login');
      } else {
        setUser(user);
      }
    };
    checkUser();
  }, [router]);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.push('/');
  };

  const menuItems = [
    { name: 'Vue d\'ensemble', icon: LayoutDashboard, href: '/dashboard' },
    { name: 'Uploader mon CV', icon: FileUp, href: '/dashboard/upload' },
    { name: 'Mes Matchs', icon: Search, href: '/dashboard/matches' },
    { name: 'Suivi candidatures', icon: Bookmark, href: '/dashboard/tracking' },
    { name: 'Mon Profil', icon: UserIcon, href: '/dashboard/profile' },
  ];

  if (!user) return null;

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--background)' }}>
      {/* Sidebar Desktop */}
      <aside className="glass desktop-sidebar" style={{ 
        width: '280px', 
        borderRight: '1px solid var(--card-border)',
        display: 'none',
        flexDirection: 'column',
        padding: '2rem 1rem'
      }}>
        <div style={{ marginBottom: '3rem', padding: '0 1rem' }}>
          <Link href="/" style={{ fontSize: '1.5rem', fontWeight: 800, background: 'linear-gradient(135deg, var(--primary), var(--secondary))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            StageMatch
          </Link>
        </div>

        <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {menuItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link 
                key={item.href} 
                href={item.href}
                className={isActive ? 'btn-primary' : ''}
                style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '0.75rem', 
                  padding: '0.75rem 1rem', 
                  borderRadius: 'var(--radius-sm)',
                  color: isActive ? 'white' : 'var(--text-secondary)',
                  background: isActive ? 'linear-gradient(135deg, var(--primary), var(--accent))' : 'transparent',
                  fontWeight: isActive ? 600 : 500,
                  transition: 'all 0.2s ease'
                }}
              >
                <item.icon size={20} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        <div style={{ marginTop: 'auto', borderTop: '1px solid var(--card-border)', paddingTop: '1.5rem' }}>
          <button 
            onClick={handleLogout}
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '0.75rem', 
              padding: '0.75rem 1rem', 
              width: '100%',
              background: 'transparent',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              fontWeight: 500
            }}
          >
            <LogOut size={20} />
            Déconnexion
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main style={{ flex: 1, padding: '2rem', maxWidth: '100vw' }}>
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3rem' }}>
          <div>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>
              Bonjour, {user.user_metadata?.full_name || 'Candidat'} 👋
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Prêt à matcher avec votre futur stage ?</p>
          </div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
             <button className="card" style={{ padding: '0.5rem', borderRadius: '50%', display: 'flex', alignItems: 'center' }}>
               <Settings size={20} color="var(--text-secondary)" />
             </button>
             <div className="card" style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
               {user.user_metadata?.full_name?.charAt(0) || user.email?.charAt(0).toUpperCase()}
             </div>
          </div>
        </header>

        {children}
      </main>

      <style jsx>{`
        @media (min-width: 1024px) {
          .desktop-sidebar {
            display: flex !important;
          }
        }
      `}</style>
    </div>
  );
}

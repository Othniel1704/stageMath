'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import {
  Bookmark,
  CheckCircle,
  ExternalLink,
  Inbox,
  type LucideIcon,
  Loader2,
  MapPin,
  Search,
  Send,
  Trash2,
} from 'lucide-react';

import { supabase } from '@/lib/supabase';

type TrackingJob = {
  id: string;
  title: string;
  company_name: string;
  location: string;
  url: string;
  contract_type?: string;
  description?: string;
  source?: string;
};

type TrackingItem = {
  id: string;
  status: 'saved' | 'applied';
  created_at: string;
  job_offers: TrackingJob;
};

export default function ApplicationTracking() {
  const [items, setItems] = useState<TrackingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'saved' | 'applied'>('saved');
  const [search, setSearch] = useState('');
  const [toast, setToast] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/applications/dashboard`, {
        headers: {
          Authorization: `Bearer ${session?.access_token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Impossible de charger le suivi');
      }

      const data = await response.json();
      setItems(data.applications || []);
    } catch (err) {
      console.error('Erreur suivi:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const stats = useMemo(() => {
    const saved = items.filter((item) => item.status === 'saved').length;
    const applied = items.filter((item) => item.status === 'applied').length;
    return {
      saved,
      applied,
      total: items.length,
    };
  }, [items]);

  const visibleItems = useMemo(() => {
    const query = search.trim().toLowerCase();
    return items
      .filter((item) => item.status === activeTab)
      .filter((item) => {
        const job = item.job_offers;
        const haystack = [job.title, job.company_name, job.location, job.contract_type, job.source, job.description]
          .join(' ')
          .toLowerCase();
        return !query || haystack.includes(query);
      });
  }, [activeTab, items, search]);

  const handleStatusUpdate = async (jobId: string, hasApplied: boolean) => {
    try {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/applications/apply/${jobId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({ has_applied: hasApplied }),
      });

      if (!response.ok) {
        throw new Error('Impossible de mettre a jour le statut');
      }

      setToast(hasApplied ? 'Offre marquee comme postulee.' : 'Offre remise dans a postuler.');
      window.setTimeout(() => setToast(null), 2500);
      fetchData();
    } catch (err) {
      setToast(err instanceof Error ? err.message : 'Erreur de mise a jour');
      window.setTimeout(() => setToast(null), 2500);
    }
  };

  const handleDelete = async (jobId: string) => {
    if (!confirm('Supprimer cette offre de votre suivi ?')) return;

    try {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/applications/${jobId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${session?.access_token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Impossible de supprimer cette offre');
      }

      setToast('Offre retiree du suivi.');
      window.setTimeout(() => setToast(null), 2500);
      fetchData();
    } catch (err) {
      setToast(err instanceof Error ? err.message : 'Erreur de suppression');
      window.setTimeout(() => setToast(null), 2500);
    }
  };

  return (
    <div style={{ display: 'grid', gap: '1.5rem' }}>
      <section
        className="card"
        style={{
          padding: '1.75rem',
          background: 'linear-gradient(135deg, rgba(56, 189, 248, 0.14), rgba(15, 23, 42, 0.94))',
        }}
      >
        <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Suivi des candidatures</h2>
        <p style={{ color: 'var(--text-secondary)', maxWidth: '70ch' }}>
          Enregistrez une offre pour y revenir plus tard, puis faites-la avancer jusqu&apos;a l&apos;etat postulee.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginTop: '1.5rem' }}>
          <TrackingStat icon={Bookmark} label="A postuler" value={stats.saved} tone="#7dd3fc" />
          <TrackingStat icon={Send} label="Postulees" value={stats.applied} tone="#34d399" />
          <TrackingStat icon={CheckCircle} label="Total suivi" value={stats.total} tone="#f8b46d" />
        </div>
      </section>

      <section className="card" style={{ padding: '1.1rem' }}>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <button onClick={() => setActiveTab('saved')} className={activeTab === 'saved' ? 'btn btn-primary' : 'btn glass'}>
              <Bookmark size={16} />
              A postuler plus tard
            </button>
            <button onClick={() => setActiveTab('applied')} className={activeTab === 'applied' ? 'btn btn-primary' : 'btn glass'}>
              <Send size={16} />
              Deja postulees
            </button>
          </div>

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.6rem',
              padding: '0.8rem 0.95rem',
              minWidth: '280px',
              borderRadius: '14px',
              border: '1px solid var(--card-border)',
              background: 'rgba(255,255,255,0.02)',
            }}
          >
            <Search size={16} color="var(--text-muted)" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Rechercher une offre suivie..."
              style={{ width: '100%', border: 'none', background: 'transparent', color: 'white', outline: 'none' }}
            />
          </div>
        </div>
      </section>

      {loading ? (
        <div className="card" style={{ minHeight: '280px', display: 'grid', placeItems: 'center' }}>
          <Loader2 className="animate-spin" size={36} color="var(--primary)" />
        </div>
      ) : visibleItems.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3.5rem' }}>
          <Inbox size={46} color="var(--text-muted)" style={{ marginBottom: '1rem' }} />
          <h3 style={{ marginBottom: '0.5rem' }}>
            {activeTab === 'saved' ? 'Aucune offre en attente' : 'Aucune offre marquee comme postulee'}
          </h3>
          <p style={{ color: 'var(--text-secondary)' }}>
            {activeTab === 'saved'
              ? 'Enregistrez une offre depuis le matching ou le catalogue pour y revenir plus tard.'
              : 'Quand vous aurez postule a une offre sauvegardee, elle apparaitra ici.'}
          </p>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '1rem' }}>
          <AnimatePresence initial={false}>
            {visibleItems.map((item) => {
              const job = item.job_offers;

              return (
                <motion.article
                  key={item.id}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 16 }}
                  className="card glass"
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'minmax(0, 1.7fr) minmax(220px, 0.9fr)',
                    gap: '1rem',
                    alignItems: 'center',
                  }}
                  layout
                >
                  <div style={{ display: 'grid', gap: '0.75rem' }}>
                    <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                      <div
                        style={{
                          width: '48px',
                          height: '48px',
                          borderRadius: '14px',
                          background: 'linear-gradient(135deg, rgba(56,189,248,0.2), rgba(249,115,22,0.18))',
                          display: 'grid',
                          placeItems: 'center',
                          fontWeight: 800,
                        }}
                      >
                        {job.company_name.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <h3 style={{ margin: 0, fontSize: '1.08rem' }}>{job.title}</h3>
                        <p style={{ color: '#f8b46d', fontWeight: 700 }}>{job.company_name}</p>
                        <div style={{ display: 'flex', gap: '0.8rem', flexWrap: 'wrap', color: 'var(--text-secondary)', fontSize: '0.87rem', marginTop: '0.35rem' }}>
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                            <MapPin size={14} />
                            {job.location}
                          </span>
                          {job.contract_type && <span>{job.contract_type}</span>}
                          {job.source && <span>{job.source}</span>}
                          <span>
                            Ajoutee le {new Date(item.created_at).toLocaleDateString('fr-FR')}
                          </span>
                        </div>
                      </div>
                    </div>

                    {job.description && (
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem' }}>
                        {job.description.length > 220 ? `${job.description.slice(0, 220).trim()}...` : job.description}
                      </p>
                    )}
                  </div>

                  <div style={{ display: 'grid', gap: '0.75rem' }}>
                    <a href={job.url} target="_blank" className="btn btn-primary" style={{ width: '100%' }}>
                      Voir l&apos;offre
                      <ExternalLink size={15} />
                    </a>

                    {activeTab === 'saved' ? (
                      <button onClick={() => handleStatusUpdate(job.id, true)} className="btn glass" style={{ width: '100%' }}>
                        <CheckCircle size={16} />
                        Marquer comme postulee
                      </button>
                    ) : (
                      <button onClick={() => handleStatusUpdate(job.id, false)} className="btn glass" style={{ width: '100%' }}>
                        <Bookmark size={16} />
                        Revenir dans a postuler
                      </button>
                    )}

                    <button onClick={() => handleDelete(job.id)} className="btn" style={{ width: '100%', color: 'var(--error)' }}>
                      <Trash2 size={16} />
                      Retirer du suivi
                    </button>
                  </div>
                </motion.article>
              );
            })}
          </AnimatePresence>
        </div>
      )}

      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            style={{
              position: 'fixed',
              bottom: '1.5rem',
              right: '1.5rem',
              background: 'linear-gradient(135deg, #0f766e, #0f172a)',
              color: 'white',
              padding: '0.9rem 1.2rem',
              borderRadius: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              boxShadow: '0 16px 28px rgba(0,0,0,0.28)',
              zIndex: 1000,
            }}
          >
            <CheckCircle size={17} />
            {toast}
          </motion.div>
        )}
      </AnimatePresence>

      <style jsx>{`
        @media (max-width: 860px) {
          article.card {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}

function TrackingStat({
  icon: Icon,
  label,
  value,
  tone,
}: {
  icon: LucideIcon;
  label: string;
  value: number;
  tone: string;
}) {
  return (
    <div
      className="glass"
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.8rem',
        padding: '1rem',
        borderRadius: '18px',
        border: '1px solid rgba(255,255,255,0.06)',
      }}
    >
      <div
        style={{
          width: '42px',
          height: '42px',
          borderRadius: '14px',
          background: `${tone}22`,
          display: 'grid',
          placeItems: 'center',
        }}
      >
        <Icon size={18} color={tone} />
      </div>
      <div>
        <div style={{ fontSize: '1.1rem', fontWeight: 800 }}>{value}</div>
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.82rem' }}>{label}</div>
      </div>
    </div>
  );
}

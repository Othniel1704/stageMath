'use client';

import type { CSSProperties } from 'react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { AnimatePresence, motion } from 'framer-motion';
import {
  AlertCircle,
  ArrowUpDown,
  Bookmark,
  Briefcase,
  CheckCircle,
  ExternalLink,
  Filter,
  Loader2,
  MapPin,
  RefreshCcw,
  Search,
  Sparkles,
  Target,
  Trophy,
  Send,
} from 'lucide-react';

import { supabase } from '@/lib/supabase';

type ScoreBreakdown = {
  semantic: number;
  skills: number;
  location: number;
  contract: number;
};

type Job = {
  id: string;
  title: string;
  company_name: string;
  location: string;
  url: string;
  contract_type: string;
  match_score: number;
  skills_required: string[];
  source: string;
  score_color: string;
  score_label?: string;
  summary?: string;
  matching_reasons?: string[];
  score_breakdown?: ScoreBreakdown;
  matched_skills?: string[];
};

type SavedState = 'idle' | 'saved' | 'applied';

const SORT_OPTIONS = [
  { value: 'score', label: 'Meilleur score' },
  { value: 'skills', label: 'Competences proches' },
  { value: 'title', label: 'Titre A-Z' },
];

const scoreTone = (score: number) => {
  if (score >= 80) return { badge: '#10b981', bg: 'rgba(16, 185, 129, 0.16)', label: 'Excellent fit' };
  if (score >= 65) return { badge: '#38bdf8', bg: 'rgba(56, 189, 248, 0.16)', label: 'Tres solide' };
  if (score >= 45) return { badge: '#f59e0b', bg: 'rgba(245, 158, 11, 0.16)', label: 'A explorer' };
  return { badge: '#f97316', bg: 'rgba(249, 115, 22, 0.16)', label: 'Secondaire' };
};

const formatModeCopy = (mode: 'match' | 'catalog') =>
  mode === 'match'
    ? {
        title: 'Matching intelligent',
        subtitle: "Des offres classees selon votre CV, vos competences et vos preferences.",
        cta: 'Recalculer mes matchs',
      }
    : {
        title: 'Catalogue des offres',
        subtitle: 'Explorez toutes les opportunites disponibles avec les memes outils de tri et de lecture.',
        cta: 'Rafraichir le catalogue',
      };

export default function JobMatches() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<'match' | 'catalog'>('match');
  const [toast, setToast] = useState<string | null>(null);
  const [savedStates, setSavedStates] = useState<Record<string, SavedState>>({});
  const [filters, setFilters] = useState({
    contract: '',
    location: '',
    search: '',
    minScore: 0,
    sortBy: 'score',
  });

  const fetchJobs = useCallback(async (nextMode = mode) => {
    setLoading(true);
    setError(null);

    try {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      const endpoint = nextMode === 'match' ? '/match' : '/jobs';
      const url = `${process.env.NEXT_PUBLIC_API_URL}${endpoint}`;

      const response = await fetch(url, {
        method: nextMode === 'match' ? 'POST' : 'GET',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session?.access_token}`,
        },
        ...(nextMode === 'match'
          ? {
              body: JSON.stringify({
                location: filters.location || null,
                preferred_contract: filters.contract || null,
                page: 1,
                page_size: 60,
              }),
            }
          : {}),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Erreur lors de la recuperation des offres");
      }

      const data = await response.json();
      setJobs(data.jobs || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur inconnue');
    } finally {
      setLoading(false);
    }
  }, [filters.contract, filters.location, mode]);

  const fetchSavedStates = useCallback(async () => {
    try {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/applications/status-map`, {
        headers: {
          Authorization: `Bearer ${session?.access_token}`,
        },
      });

      if (!response.ok) {
        return;
      }

      const data = await response.json();
      const nextStates: Record<string, SavedState> = {};
      for (const jobId of data.saved_job_ids || []) {
        nextStates[jobId] = 'saved';
      }
      for (const jobId of data.applied_job_ids || []) {
        nextStates[jobId] = 'applied';
      }
      setSavedStates(nextStates);
    } catch (err) {
      console.error('Erreur status-map:', err);
    }
  }, []);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  useEffect(() => {
    fetchSavedStates();
  }, [fetchSavedStates]);

  const visibleJobs = useMemo(() => {
    const query = filters.search.trim().toLowerCase();
    const filtered = jobs.filter((job) => {
      const searchableText = [
        job.title,
        job.company_name,
        job.location,
        job.contract_type,
        job.summary,
        ...(job.skills_required || []),
        ...(job.matched_skills || []),
      ]
        .join(' ')
        .toLowerCase();

      const scoreOk = mode === 'catalog' || job.match_score >= filters.minScore;
      const searchOk = !query || searchableText.includes(query);
      return scoreOk && searchOk;
    });

    return filtered.sort((a, b) => {
      if (filters.sortBy === 'title') {
        return a.title.localeCompare(b.title);
      }
      if (filters.sortBy === 'skills') {
        return (b.matched_skills?.length || 0) - (a.matched_skills?.length || 0);
      }
      return b.match_score - a.match_score;
    });
  }, [filters.minScore, filters.search, filters.sortBy, jobs, mode]);

  const stats = useMemo(() => {
    const total = visibleJobs.length;
    const strong = visibleJobs.filter((job) => job.match_score >= 70).length;
    const appliedFilters =
      Number(Boolean(filters.contract)) +
      Number(Boolean(filters.location)) +
      Number(Boolean(filters.search)) +
      Number(filters.minScore > 0);

    return { total, strong, appliedFilters };
  }, [filters, visibleJobs]);

  const handleSaveJob = async (jobId: string) => {
    try {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/applications/save/${jobId}`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${session?.access_token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Impossible d'enregistrer l'offre");
      }

      setSavedStates((current) => ({ ...current, [jobId]: 'saved' }));
      setToast('Offre ajoutee a votre suivi.');
      window.setTimeout(() => setToast(null), 2500);
    } catch (err) {
      setToast(err instanceof Error ? err.message : 'Erreur de sauvegarde');
      window.setTimeout(() => setToast(null), 2500);
    }
  };

  const copy = formatModeCopy(mode);

  const handleApplyFromCard = async (jobId: string) => {
    try {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (savedStates[jobId] !== 'saved') {
        await fetch(`${process.env.NEXT_PUBLIC_API_URL}/applications/save/${jobId}`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${session?.access_token}`,
          },
        });
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/applications/apply/${jobId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({ has_applied: true }),
      });

      if (!response.ok) {
        throw new Error("Impossible de mettre l'offre en postulee");
      }

      setSavedStates((current) => ({ ...current, [jobId]: 'applied' }));
      setToast('Offre marquee comme postulee.');
      window.setTimeout(() => setToast(null), 2500);
    } catch (err) {
      setToast(err instanceof Error ? err.message : 'Erreur de suivi');
      window.setTimeout(() => setToast(null), 2500);
    }
  };

  return (
    <div style={{ display: 'grid', gap: '1.5rem' }}>
      <section
        className="card"
        style={{
          padding: '1.75rem',
          background:
            'linear-gradient(135deg, rgba(14, 116, 144, 0.22), rgba(249, 115, 22, 0.12) 55%, rgba(15, 23, 42, 0.92))',
          borderColor: 'rgba(125, 211, 252, 0.2)',
        }}
      >
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            gap: '1rem',
            alignItems: 'flex-start',
            flexWrap: 'wrap',
          }}
        >
          <div style={{ maxWidth: '760px' }}>
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.4rem 0.8rem',
                borderRadius: '999px',
                background: 'rgba(255,255,255,0.08)',
                marginBottom: '1rem',
                color: '#bae6fd',
                fontSize: '0.82rem',
                fontWeight: 700,
              }}
            >
              <Sparkles size={15} />
              Matching + exploration des offres
            </div>
            <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{copy.title}</h2>
            <p style={{ color: 'var(--text-secondary)', maxWidth: '65ch' }}>{copy.subtitle}</p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <div
              className="glass"
              style={{ display: 'flex', padding: '0.3rem', borderRadius: '999px', border: '1px solid var(--card-border)' }}
            >
              <button
                onClick={() => setMode('match')}
                style={modeButtonStyle(mode === 'match')}
              >
                Mes matchs
              </button>
              <button
                onClick={() => setMode('catalog')}
                style={modeButtonStyle(mode === 'catalog')}
              >
                Catalogue
              </button>
            </div>

            <button onClick={() => fetchJobs()} className="btn btn-primary">
              <RefreshCcw size={16} />
              {copy.cta}
            </button>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginTop: '1.5rem' }}>
          <StatCard icon={Target} label="Offres visibles" value={String(stats.total)} />
          <StatCard icon={Trophy} label="Scores forts" value={String(stats.strong)} />
          <StatCard icon={Filter} label="Filtres actifs" value={String(stats.appliedFilters)} />
        </div>
      </section>

      <section className="card" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr 1fr', gap: '0.9rem' }} className="matches-filters">
          <label style={fieldStyle}>
            <span style={labelStyle}>Recherche</span>
            <div style={inputShellStyle}>
              <Search size={16} color="var(--text-muted)" />
              <input
                value={filters.search}
                onChange={(e) => setFilters((current) => ({ ...current, search: e.target.value }))}
                placeholder="Titre, entreprise, competences..."
                style={inputStyle}
              />
            </div>
          </label>

          <label style={fieldStyle}>
            <span style={labelStyle}>Contrat</span>
            <select
              value={filters.contract}
              onChange={(e) => setFilters((current) => ({ ...current, contract: e.target.value }))}
              style={selectStyle}
            >
              <option value="">Tous</option>
              <option value="stage">Stage</option>
              <option value="alternance">Alternance</option>
            </select>
          </label>

          <label style={fieldStyle}>
            <span style={labelStyle}>Localisation</span>
            <input
              value={filters.location}
              onChange={(e) => setFilters((current) => ({ ...current, location: e.target.value }))}
              placeholder="Paris, Lyon, remote..."
              style={selectStyle}
            />
          </label>

          <label style={fieldStyle}>
            <span style={labelStyle}>Score minimum</span>
            <select
              value={filters.minScore}
              onChange={(e) => setFilters((current) => ({ ...current, minScore: Number(e.target.value) }))}
              style={selectStyle}
              disabled={mode === 'catalog'}
            >
              <option value={0}>Aucun</option>
              <option value={40}>40+</option>
              <option value={60}>60+</option>
              <option value={75}>75+</option>
            </select>
          </label>

          <label style={fieldStyle}>
            <span style={labelStyle}>Tri</span>
            <div style={inputShellStyle}>
              <ArrowUpDown size={16} color="var(--text-muted)" />
              <select
                value={filters.sortBy}
                onChange={(e) => setFilters((current) => ({ ...current, sortBy: e.target.value }))}
                style={selectInsideShellStyle}
              >
                {SORT_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </label>
        </div>
      </section>

      {loading ? (
        <div className="card" style={{ minHeight: '320px', display: 'grid', placeItems: 'center' }}>
          <div style={{ textAlign: 'center' }}>
            <Loader2 size={42} className="animate-spin" color="var(--primary)" />
            <p style={{ color: 'var(--text-secondary)', marginTop: '1rem' }}>
              {mode === 'match' ? 'Calcul des matchs en cours...' : 'Chargement des offres...'}
            </p>
          </div>
        </div>
      ) : error ? (
        <div className="card" style={{ textAlign: 'center', padding: '3.5rem' }}>
          <AlertCircle size={48} color="var(--error)" style={{ marginBottom: '1rem' }} />
          <h3 style={{ marginBottom: '0.5rem' }}>Impossible de charger les offres</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>{error}</p>
          <button onClick={() => fetchJobs()} className="btn glass">
            <RefreshCcw size={16} />
            Reessayer
          </button>
        </div>
      ) : visibleJobs.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3.5rem' }}>
          <Search size={48} color="var(--text-muted)" style={{ marginBottom: '1rem' }} />
          <h3 style={{ marginBottom: '0.5rem' }}>Aucune offre ne correspond a vos criteres</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
            Essayez d&apos;enlever quelques filtres, de changer de localisation, ou de completer votre profil pour obtenir un matching plus pertinent.
          </p>
          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button
              className="btn glass"
              onClick={() => setFilters({ contract: '', location: '', search: '', minScore: 0, sortBy: 'score' })}
            >
              Reinitialiser les filtres
            </button>
            <Link href="/dashboard/profile" className="btn btn-primary">
              Completer mon profil
            </Link>
          </div>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '1rem' }}>
          <AnimatePresence initial={false}>
            {visibleJobs.map((job, index) => {
              const tone = scoreTone(job.match_score);
              const breakdown = job.score_breakdown || { semantic: 0, skills: 0, location: 0, contract: 0 };
              const savedState = savedStates[job.id] || 'idle';

              return (
                <motion.article
                  key={job.id}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.03 }}
                  className="card"
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'minmax(0, 1.8fr) minmax(280px, 1fr)',
                    gap: '1.25rem',
                    alignItems: 'stretch',
                  }}
                  layout
                >
                  <div style={{ display: 'grid', gap: '1rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
                      <div style={{ display: 'flex', gap: '1rem' }}>
                        <div
                          style={{
                            width: '56px',
                            height: '56px',
                            borderRadius: '18px',
                            display: 'grid',
                            placeItems: 'center',
                            background: 'linear-gradient(135deg, rgba(249, 115, 22, 0.25), rgba(14, 165, 233, 0.18))',
                            border: '1px solid rgba(255,255,255,0.08)',
                            fontSize: '1.2rem',
                            fontWeight: 800,
                          }}
                        >
                          {job.company_name.charAt(0).toUpperCase()}
                        </div>

                        <div>
                          <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'center', flexWrap: 'wrap', marginBottom: '0.35rem' }}>
                            <h3 style={{ margin: 0, fontSize: '1.15rem' }}>{job.title}</h3>
                            {mode === 'match' && (
                              <span
                                style={{
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  gap: '0.35rem',
                                  padding: '0.2rem 0.6rem',
                                  borderRadius: '999px',
                                  background: tone.bg,
                                  color: tone.badge,
                                  fontSize: '0.75rem',
                                  fontWeight: 700,
                                }}
                              >
                                <Sparkles size={13} />
                                {tone.label}
                              </span>
                            )}
                          </div>
                          <p style={{ color: '#f8b46d', fontWeight: 700, marginBottom: '0.6rem' }}>{job.company_name}</p>
                          <div style={{ display: 'flex', gap: '0.9rem', flexWrap: 'wrap', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                            <span style={metaStyle}>
                              <MapPin size={14} />
                              {job.location}
                            </span>
                            <span style={metaStyle}>
                              <Briefcase size={14} />
                              {job.contract_type}
                            </span>
                            <span style={metaStyle}>
                              <Target size={14} />
                              {job.source}
                            </span>
                            {savedState !== 'idle' && (
                              <span
                                style={{
                                  ...metaStyle,
                                  padding: '0.2rem 0.55rem',
                                  borderRadius: '999px',
                                  background: savedState === 'applied' ? 'rgba(16,185,129,0.14)' : 'rgba(56,189,248,0.14)',
                                  color: savedState === 'applied' ? '#34d399' : '#7dd3fc',
                                  border: '1px solid rgba(255,255,255,0.06)',
                                }}
                              >
                                {savedState === 'applied' ? <Send size={13} /> : <Bookmark size={13} />}
                                {savedState === 'applied' ? 'Postulee' : 'Enregistree'}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      <div
                        style={{
                          minWidth: '120px',
                          borderRadius: '18px',
                          padding: '0.9rem 1rem',
                          background: tone.bg,
                          border: `1px solid ${tone.badge}33`,
                          alignSelf: 'flex-start',
                        }}
                      >
                        <div style={{ color: tone.badge, fontSize: '1.55rem', fontWeight: 800, lineHeight: 1 }}>{mode === 'catalog' ? 'N/A' : `${job.match_score}%`}</div>
                        <div style={{ color: 'var(--text-secondary)', fontSize: '0.78rem', marginTop: '0.35rem' }}>
                          {mode === 'catalog' ? 'Catalogue brut' : 'Score global'}
                        </div>
                      </div>
                    </div>

                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.96rem' }}>{job.summary || 'Description non disponible.'}</p>

                    {!!job.matching_reasons?.length && (
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.6rem' }}>
                        {job.matching_reasons.map((reason) => (
                          <span
                            key={reason}
                            style={{
                              padding: '0.45rem 0.7rem',
                              borderRadius: '999px',
                              background: 'rgba(255,255,255,0.05)',
                              border: '1px solid rgba(255,255,255,0.06)',
                              color: 'var(--text-primary)',
                              fontSize: '0.78rem',
                            }}
                          >
                            {reason}
                          </span>
                        ))}
                      </div>
                    )}

                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                      {(job.matched_skills?.length ? job.matched_skills : job.skills_required.slice(0, 6)).map((skill) => (
                        <span
                          key={`${job.id}-${skill}`}
                          style={{
                            fontSize: '0.8rem',
                            background: 'rgba(14, 165, 233, 0.12)',
                            color: '#7dd3fc',
                            padding: '0.35rem 0.65rem',
                            borderRadius: '999px',
                            border: '1px solid rgba(125, 211, 252, 0.16)',
                          }}
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div
                    className="glass"
                    style={{
                      padding: '1rem',
                      borderRadius: '20px',
                      display: 'grid',
                      gap: '0.9rem',
                      border: '1px solid rgba(255,255,255,0.06)',
                    }}
                  >
                    <div>
                      <h4 style={{ fontSize: '0.95rem', marginBottom: '0.75rem' }}>Lecture du score</h4>
                      <ScoreRow label="Semantique" value={breakdown.semantic} />
                      <ScoreRow label="Competences" value={breakdown.skills} />
                      <ScoreRow label="Localisation" value={breakdown.location} />
                      <ScoreRow label="Contrat" value={breakdown.contract} />
                    </div>

                    <div style={{ display: 'flex', gap: '0.75rem', marginTop: 'auto', flexWrap: 'wrap' }}>
                      <a href={job.url} target="_blank" className="btn btn-primary" style={{ flex: 1, minWidth: '160px' }}>
                        Postuler
                        <ExternalLink size={15} />
                      </a>
                      <button
                        onClick={() => {
                          if (savedState === 'idle') {
                            handleSaveJob(job.id);
                          } else if (savedState === 'saved') {
                            handleApplyFromCard(job.id);
                          }
                        }}
                        className="btn glass"
                        style={{ minWidth: '180px' }}
                        disabled={savedState === 'applied'}
                      >
                        {savedState === 'idle' ? <Bookmark size={16} /> : <Send size={16} />}
                        {savedState === 'idle'
                          ? 'Garder pour plus tard'
                          : savedState === 'saved'
                            ? 'Marquer postulee'
                            : 'Deja postulee'}
                      </button>
                    </div>
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
            initial={{ opacity: 0, y: 32 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 32 }}
            style={{
              position: 'fixed',
              bottom: '1.5rem',
              right: '1.5rem',
              background: 'linear-gradient(135deg, #0f766e, #0f172a)',
              color: 'white',
              padding: '0.95rem 1.2rem',
              borderRadius: '16px',
              boxShadow: '0 18px 30px rgba(0,0,0,0.28)',
              zIndex: 1000,
              display: 'flex',
              alignItems: 'center',
              gap: '0.6rem',
              border: '1px solid rgba(255,255,255,0.08)',
            }}
          >
            <CheckCircle size={18} />
            <span>{toast}</span>
          </motion.div>
        )}
      </AnimatePresence>

      <style jsx>{`
        @media (max-width: 1080px) {
          .matches-filters {
            grid-template-columns: 1fr 1fr !important;
          }
        }

        @media (max-width: 860px) {
          article.card {
            grid-template-columns: 1fr !important;
          }
        }

        @media (max-width: 720px) {
          .matches-filters {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Target;
  label: string;
  value: string;
}) {
  return (
    <div
      className="glass"
      style={{
        borderRadius: '18px',
        padding: '1rem',
        border: '1px solid rgba(255,255,255,0.06)',
        display: 'flex',
        alignItems: 'center',
        gap: '0.85rem',
      }}
    >
      <div
        style={{
          width: '42px',
          height: '42px',
          borderRadius: '14px',
          background: 'rgba(255,255,255,0.08)',
          display: 'grid',
          placeItems: 'center',
        }}
      >
        <Icon size={18} color="#bae6fd" />
      </div>
      <div>
        <div style={{ fontSize: '1.15rem', fontWeight: 800 }}>{value}</div>
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.82rem' }}>{label}</div>
      </div>
    </div>
  );
}

function ScoreRow({ label, value }: { label: string; value: number }) {
  return (
    <div style={{ marginBottom: '0.7rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem', fontSize: '0.83rem' }}>
        <span style={{ color: 'var(--text-secondary)' }}>{label}</span>
        <strong>{value}%</strong>
      </div>
      <div style={{ height: '7px', borderRadius: '999px', background: 'rgba(255,255,255,0.07)', overflow: 'hidden' }}>
        <div
          style={{
            width: `${Math.max(4, value)}%`,
            height: '100%',
            borderRadius: '999px',
            background: 'linear-gradient(90deg, #38bdf8, #f97316)',
          }}
        />
      </div>
    </div>
  );
}

const fieldStyle: CSSProperties = {
  display: 'grid',
  gap: '0.4rem',
};

const labelStyle: CSSProperties = {
  color: 'var(--text-secondary)',
  fontSize: '0.82rem',
  fontWeight: 600,
};

const inputShellStyle: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '0.55rem',
  padding: '0.8rem 0.9rem',
  borderRadius: '14px',
  border: '1px solid var(--card-border)',
  background: 'rgba(255,255,255,0.02)',
};

const inputStyle: CSSProperties = {
  width: '100%',
  border: 'none',
  background: 'transparent',
  color: 'white',
  outline: 'none',
  fontSize: '0.95rem',
};

const selectStyle: CSSProperties = {
  padding: '0.85rem 0.9rem',
  borderRadius: '14px',
  border: '1px solid var(--card-border)',
  background: 'rgba(255,255,255,0.02)',
  color: 'white',
  outline: 'none',
};

const selectInsideShellStyle: CSSProperties = {
  width: '100%',
  border: 'none',
  background: 'transparent',
  color: 'white',
  outline: 'none',
};

const metaStyle: CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: '0.35rem',
};

const modeButtonStyle = (active: boolean): CSSProperties => ({
  padding: '0.55rem 0.95rem',
  borderRadius: '999px',
  border: 'none',
  background: active ? 'linear-gradient(135deg, #0ea5e9, #f97316)' : 'transparent',
  color: 'white',
  cursor: 'pointer',
  fontWeight: 700,
  fontSize: '0.84rem',
});

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { AlertCircle, CheckCircle2, ChevronRight, FileUp, Loader2, Sparkles } from 'lucide-react';

import { supabase } from '@/lib/supabase';

type UploadResult = {
  profile_saved: boolean;
  skills: string[];
  candidate_name?: string;
  candidate_email?: string;
};

export default function UploadCV() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.[0]) return;
    setFile(e.target.files[0]);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/upload-cv`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${session?.access_token}`,
        },
        body: formData,
      });

      const data = (await response.json()) as UploadResult & { detail?: string };

      if (!response.ok) {
        throw new Error(data.detail || "Erreur lors de l'analyse du CV");
      }

      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur inattendue');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2.5rem' }}>
        <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Analyse de CV IA</h2>
        <p style={{ color: 'var(--text-secondary)' }}>
          Uploadez votre CV pour que notre IA extraie vos competences et prepare un matching plus precis.
        </p>
      </div>

      {!result ? (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="card glass"
          style={{
            padding: '4rem 2rem',
            textAlign: 'center',
            border: '2px dashed var(--card-border)',
            borderRadius: 'var(--radius-lg)',
          }}
        >
          <div
            style={{
              width: '80px',
              height: '80px',
              borderRadius: '20px',
              background: 'rgba(99, 102, 241, 0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 2rem auto',
              color: 'var(--primary)',
            }}
          >
            <FileUp size={40} />
          </div>

          <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>
            {file ? file.name : 'Glissez-deposez votre CV ici'}
          </h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', fontSize: '0.9rem' }}>
            Formats supportes : PDF, PNG, JPG (max 5 Mo)
          </p>

          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <label className="btn glass" style={{ cursor: 'pointer' }}>
              Parcourir...
              <input type="file" hidden onChange={handleFileChange} accept=".pdf,.png,.jpg,.jpeg" />
            </label>

            {file && (
              <button onClick={handleUpload} className="btn btn-primary" disabled={uploading}>
                {uploading ? <Loader2 className="animate-spin" /> : <><Sparkles size={18} /> Analyser maintenant</>}
              </button>
            )}
          </div>

          {error && (
            <div
              style={{
                marginTop: '2rem',
                color: 'var(--error)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                fontSize: '0.9rem',
              }}
            >
              <AlertCircle size={16} /> {error}
            </div>
          )}
        </motion.div>
      ) : (
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="card" style={{ padding: '2.5rem' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
              marginBottom: '2.5rem',
              color: result.profile_saved ? 'var(--success)' : 'var(--warning)',
            }}
          >
            {result.profile_saved ? <CheckCircle2 size={32} /> : <AlertCircle size={32} />}
            <div>
              <h3 style={{ fontSize: '1.5rem', color: 'var(--text-primary)' }}>
                {result.profile_saved ? 'Profil sauvegarde !' : 'Analyse terminee'}
              </h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                {result.profile_saved
                  ? `Vos donnees sont bien enregistrees. Nous avons extrait ${result.skills.length} competences.`
                  : 'Analyse reussie, mais la sauvegarde du profil a echoue.'}
              </p>
            </div>
          </div>

          {!result.profile_saved && (
            <div
              style={{
                marginBottom: '1.5rem',
                padding: '1rem',
                background: 'rgba(239, 68, 68, 0.1)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--error)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontSize: '0.9rem',
              }}
            >
              <AlertCircle size={16} />
              Votre CV a ete analyse, mais le profil n&apos;a pas pu etre sauvegarde correctement.
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
            <div>
              <h4 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Competences detectees
              </h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
                {result.skills.map((skill) => (
                  <span
                    key={skill}
                    style={{
                      padding: '0.4rem 0.8rem',
                      borderRadius: '8px',
                      background: 'rgba(99, 102, 241, 0.1)',
                      color: 'var(--primary)',
                      fontSize: '0.85rem',
                      fontWeight: 600,
                      border: '1px solid rgba(99, 102, 241, 0.2)',
                    }}
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h4 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Informations extraites
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div className="glass" style={{ padding: '1rem', borderRadius: 'var(--radius-sm)' }}>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Nom complet</p>
                  <p style={{ fontWeight: 600 }}>{result.candidate_name || 'Non detecte'}</p>
                </div>
                <div className="glass" style={{ padding: '1rem', borderRadius: 'var(--radius-sm)' }}>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Email</p>
                  <p style={{ fontWeight: 600 }}>{result.candidate_email || 'Non detecte'}</p>
                </div>
              </div>
            </div>
          </div>

          <div
            style={{
              marginTop: '3rem',
              paddingTop: '2rem',
              borderTop: '1px solid var(--card-border)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '1rem',
            }}
          >
            <button onClick={() => setResult(null)} className="btn glass">
              Re-uploader
            </button>
            <Link href="/dashboard/matches" className="btn btn-primary">
              Voir mes matchs <ChevronRight size={18} />
            </Link>
          </div>
        </motion.div>
      )}

      <div
        style={{
          marginTop: '4rem',
          padding: '2rem',
          background: 'rgba(99, 102, 241, 0.05)',
          borderRadius: 'var(--radius-lg)',
          display: 'flex',
          gap: '1.5rem',
          alignItems: 'center',
        }}
      >
        <div
          style={{
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            background: 'var(--primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            flexShrink: 0,
          }}
        >
          <Sparkles size={24} />
        </div>
        <div>
          <h4 style={{ marginBottom: '0.25rem' }}>Comment l&apos;IA analyse votre CV ?</h4>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            Nous utilisons des modeles NLP pour detecter technologies, outils et experiences afin de produire un matching utile et lisible.
          </p>
        </div>
      </div>
    </div>
  );
}

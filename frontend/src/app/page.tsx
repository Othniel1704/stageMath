'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { ChevronRight, Rocket, Shield, Target, Zap } from 'lucide-react';

export default function Home() {
  return (
    <div className="landing-page">
      <nav className="glass" style={{ position: 'fixed', top: 0, width: '100%', zIndex: 100, height: 'var(--header-height)' }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '100%' }}>
          <div
            className="logo"
            style={{
              fontSize: '1.5rem',
              fontWeight: 800,
              background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            StageMatch
          </div>
          <div className="nav-links" style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
            <Link href="/about" style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', fontWeight: 500 }}>
              Comment ca marche
            </Link>
            <Link href="/login" className="btn" style={{ fontSize: '0.9rem', color: 'var(--text-primary)' }}>
              Connexion
            </Link>
            <Link href="/signup" className="btn btn-primary" style={{ fontSize: '0.9rem' }}>
              S&apos;inscrire
            </Link>
          </div>
        </div>
      </nav>

      <main>
        <section style={{ paddingTop: 'calc(var(--header-height) + 4rem)', paddingBottom: '6rem' }}>
          <div className="container" style={{ textAlign: 'center' }}>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
              <span
                style={{
                  background: 'rgba(99, 102, 241, 0.1)',
                  color: 'var(--primary)',
                  padding: '0.5rem 1rem',
                  borderRadius: '100px',
                  fontSize: '0.8rem',
                  fontWeight: 700,
                  marginBottom: '1.5rem',
                  display: 'inline-block',
                  border: '1px solid rgba(99, 102, 241, 0.2)',
                }}
              >
                Propulse par l&apos;intelligence artificielle
              </span>
              <h1 style={{ fontSize: 'clamp(2.5rem, 8vw, 4.5rem)', marginBottom: '1.5rem' }} className="text-gradient">
                Decrochez le stage de <br /> vos reves en un clic.
              </h1>
              <p style={{ color: 'var(--text-secondary)', fontSize: '1.25rem', maxWidth: '700px', margin: '0 auto 2.5rem auto' }}>
                StageMatch analyse votre CV et vous connecte instantanement aux offres qui correspondent le mieux a vos competences techniques.
              </p>
              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                <Link href="/signup" className="btn btn-primary" style={{ padding: '1rem 2rem', fontSize: '1.1rem' }}>
                  Commencer maintenant <ChevronRight size={20} />
                </Link>
                <Link href="/login" className="btn glass" style={{ padding: '1rem 2rem', fontSize: '1.1rem' }}>
                  Voir la plateforme
                </Link>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4, duration: 1 }}
              style={{ marginTop: '5rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '2rem' }}
            >
              <div className="card">
                <div style={{ color: 'var(--primary)', marginBottom: '0.5rem' }}>
                  <Rocket size={32} />
                </div>
                <h3 style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>10k+</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Offres actives</p>
              </div>
              <div className="card">
                <div style={{ color: 'var(--secondary)', marginBottom: '0.5rem' }}>
                  <Target size={32} />
                </div>
                <h3 style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>95%</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Matching de precision</p>
              </div>
              <div className="card">
                <div style={{ color: 'var(--accent)', marginBottom: '0.5rem' }}>
                  <Zap size={32} />
                </div>
                <h3 style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>2 min</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Configuration rapide</p>
              </div>
            </motion.div>
          </div>
        </section>

        <section style={{ padding: '6rem 0', background: 'rgba(15, 23, 42, 0.5)' }}>
          <div className="container">
            <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
              <h2 style={{ fontSize: '2.5rem' }}>Pourquoi choisir StageMatch ?</h2>
              <p style={{ color: 'var(--text-secondary)' }}>Une technologie concue pour accelerer votre carriere.</p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2.5rem' }}>
              <div className="card" style={{ display: 'flex', gap: '1.5rem' }}>
                <div
                  style={{
                    flexShrink: 0,
                    width: '48px',
                    height: '48px',
                    borderRadius: '12px',
                    background: 'rgba(99, 102, 241, 0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--primary)',
                  }}
                >
                  <Shield size={24} />
                </div>
                <div>
                  <h4 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>Analyse intelligente</h4>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
                    Notre IA extrait vos points forts directement depuis votre CV, meme si certains signaux sont peu visibles au premier regard.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer style={{ padding: '4rem 0', borderTop: '1px solid var(--card-border)' }}>
        <div className="container" style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          <p>© 2026 StageMatch. Concu pour les developpeurs de demain.</p>
        </div>
      </footer>
    </div>
  );
}

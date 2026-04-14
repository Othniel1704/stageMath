'use client';

import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import { motion } from 'framer-motion';
import { 
  FileCheck, 
  Briefcase, 
  TrendingUp
} from 'lucide-react';
import Link from 'next/link';

export default function Dashboard() {
  const [stats, setStats] = useState({
    matches: 0,
    applications: 0,
    profileComplete: 0
  });
  const [userData, setUserData] = useState<{name?: string, skills: string[]}>({ skills: [] });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (!session) return;

        // Fetch Stats
        const statsRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/profile/stats`, {
          headers: { 'Authorization': `Bearer ${session.access_token}` }
        });
        if (statsRes.ok) {
          const sData = await statsRes.json();
          setStats({
            matches: sData.match_count,
            applications: sData.application_count,
            profileComplete: sData.profile_completion
          });
        }

        // Fetch User Info for greeting
        const profileRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/profile/me`, {
          headers: { 'Authorization': `Bearer ${session.access_token}` }
        });
        if (profileRes.ok) {
          const pData = await profileRes.json();
          setUserData({
            name: pData.candidate_name,
            skills: pData.extracted_skills || []
          });
        }
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="dashboard-content">
      <div style={{ marginBottom: '2.5rem' }}>
        <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>
          Ravi de vous revoir, {userData.name || 'Candidat'} !
        </h2>
        <p style={{ color: 'var(--text-secondary)' }}>
          {userData.skills.length > 0 
            ? `Vos compétences (${userData.skills.slice(0, 3).join(', ')}...) sont prêtes pour le matching.`
            : 'Complétez votre profil pour découvrir vos opportunités sur mesure.'}
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(99, 102, 241, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary)' }}>
              <TrendingUp size={24} />
            </div>
          </div>
          <h3 style={{ fontSize: '1.75rem', marginBottom: '0.25rem' }}>{stats.matches}</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Matchs trouvés</p>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(236, 72, 153, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--secondary)' }}>
              <Briefcase size={24} />
            </div>
          </div>
          <h3 style={{ fontSize: '1.75rem', marginBottom: '0.25rem' }}>{stats.applications}</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Favoris / Candidatures</p>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(139, 92, 246, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent)' }}>
              <FileCheck size={24} />
            </div>
            <span style={{ fontSize: '0.8rem', color: 'var(--accent)', fontWeight: 'bold' }}>{stats.profileComplete}%</span>
          </div>
          <div style={{ width: '100%', height: '6px', background: 'var(--card-border)', borderRadius: '3px', marginBottom: '0.5rem' }}>
            <div style={{ width: `${stats.profileComplete}%`, height: '100%', background: 'var(--accent)', borderRadius: '3px' }}></div>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Profil {stats.profileComplete === 100 ? 'complet' : 'en cours'}</p>
        </motion.div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <h3 style={{ fontSize: '1.25rem' }}>Meilleurs Matchs</h3>
          
          {stats.matches > 0 ? (
            <>
              <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', background: 'linear-gradient(90deg, var(--card-bg), rgba(99, 102, 241, 0.05))' }}>
                 <div style={{ width: '56px', height: '56px', borderRadius: '12px', background: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem' }}>
                   🚀
                 </div>
                 <div style={{ flex: 1 }}>
                   <h4 style={{ fontSize: '1.1rem', marginBottom: '0.25rem' }}>Consultez vos opportunités</h4>
                   <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Cliquez sur le bouton pour voir vos matchs personnalises par l&apos;IA.</p>
                 </div>
                 <Link href="/dashboard/matches" className="btn btn-primary" style={{ padding: '0.5rem 1rem' }}>Détails</Link>
              </div>
            </>
          ) : (
            <div className="card glass" style={{ textAlign: 'center', padding: '3rem' }}>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>Aucun match calculé. Uploadez votre CV pour commencer.</p>
              <Link href="/dashboard/upload" className="btn btn-primary">Uploader mon CV</Link>
            </div>
          )}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <h3 style={{ fontSize: '1.25rem' }}>Statut du Profil</h3>
          <div className="card glass">
             <div style={{ fontSize: '0.9rem', marginBottom: '1rem' }}>
                <strong>Vérification :</strong> {stats.profileComplete === 100 ? '✅ Dossier sauvegardé' : '❌ Dossier incomplet'}
             </div>
             <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                {stats.profileComplete === 100 
                  ? 'Vos données sont sécurisées et synchronisées avec notre moteur de matching.' 
                  : 'Téléchargez votre CV pour persister vos compétences.'}
             </p>
             <Link href="/dashboard/profile" className="btn glass" style={{ width: '100%', fontSize: '0.8rem' }}>Gérer mes compétences</Link>
          </div>
        </div>
      </div>
      
      <style jsx>{`
        @media (max-width: 1024px) {
          .dashboard-content > div {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}

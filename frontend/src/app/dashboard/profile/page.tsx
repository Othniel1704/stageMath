'use client';

import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { motion } from 'framer-motion';
import { User, MapPin, Briefcase, Save, Loader2, CheckCircle, Code, X } from 'lucide-react';

export default function Profile() {
  const [profile, setProfile] = useState({
    candidate_name: '',
    location: '',
    preferred_contract: '',
    extracted_skills: [] as string[],
  });
  const [newSkill, setNewSkill] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/profile/me`, {
          headers: {
            'Authorization': `Bearer ${session?.access_token}`,
          }
        });
        if (response.ok) {
          const data = await response.json();
          setProfile({
            candidate_name: data.candidate_name || '',
            location: data.location || '',
            preferred_contract: data.preferred_contract || '',
            extracted_skills: data.extracted_skills || [],
          });
        }
      } catch (err) {
        console.error('Erreur profil:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/profile/me`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({
          candidate_name: profile.candidate_name,
          location: profile.location,
          preferred_contract: profile.preferred_contract,
          extracted_skills: profile.extracted_skills,
        })
      });
      if (response.ok) {
        setMessage('Profil mis à jour avec succès !');
        setTimeout(() => setMessage(null), 3000);
      }
    } catch (err) {
      console.error('Erreur maj profil:', err);
    } finally {
      setSaving(false);
    }
  };

  const addSkill = () => {
    if (newSkill.trim() && !profile.extracted_skills.includes(newSkill.trim())) {
      setProfile({
        ...profile,
        extracted_skills: [...profile.extracted_skills, newSkill.trim()]
      });
      setNewSkill('');
    }
  };

  const removeSkill = (skillToRemove: string) => {
    setProfile({
      ...profile,
      extracted_skills: profile.extracted_skills.filter(s => s !== skillToRemove)
    });
  };

  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}><Loader2 className="animate-spin" size={32} color="var(--primary)" /></div>;

  return (
    <div style={{ maxWidth: '800px' }}>
      <div style={{ marginBottom: '2.5rem' }}>
        <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Mon Profil</h2>
        <p style={{ color: 'var(--text-secondary)' }}>Personnalisez vos préférences et vos compétences pour un matching plus précis.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '2rem' }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="card">
          <form onSubmit={handleUpdate} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Nom complet</label>
              <div style={{ position: 'relative' }}>
                <User size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input 
                  type="text" 
                  className="glass"
                  value={profile.candidate_name}
                  onChange={(e) => setProfile({...profile, candidate_name: e.target.value})}
                  style={{ width: '100%', padding: '0.75rem 1rem 0.75rem 2.5rem', borderRadius: 'var(--radius-sm)', color: 'white', border: '1px solid var(--card-border)', outline: 'none' }}
                />
              </div>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Localisation souhaitée</label>
              <div style={{ position: 'relative' }}>
                <MapPin size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input 
                  type="text" 
                  placeholder="ex: Paris, Lyon, France entière..."
                  className="glass"
                  value={profile.location}
                  onChange={(e) => setProfile({...profile, location: e.target.value})}
                  style={{ width: '100%', padding: '0.75rem 1rem 0.75rem 2.5rem', borderRadius: 'var(--radius-sm)', color: 'white', border: '1px solid var(--card-border)', outline: 'none' }}
                />
              </div>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Type de contrat recherché</label>
              <div style={{ position: 'relative' }}>
                <Briefcase size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <select 
                  className="glass"
                  value={profile.preferred_contract}
                  onChange={(e) => setProfile({...profile, preferred_contract: e.target.value})}
                  style={{ width: '100%', padding: '0.75rem 1rem 0.75rem 2.5rem', borderRadius: 'var(--radius-sm)', color: 'white', border: '1px solid var(--card-border)', outline: 'none' }}
                >
                  <option value="">Tous les types</option>
                  <option value="stage">Stage</option>
                  <option value="alternance">Alternance / Apprentissage</option>
                </select>
              </div>
            </div>

            <div style={{ marginTop: '1rem', display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? <Loader2 className="animate-spin" /> : <><Save size={18} /> Sauvegarder</>}
              </button>
              
              {message && (
                <motion.span initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} style={{ color: 'var(--success)', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <CheckCircle size={16} /> {message}
                </motion.span>
              )}
            </div>
          </form>
        </motion.div>

        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="card glass">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', color: 'var(--primary)' }}>
            <Code size={20} />
            <h3 style={{ fontSize: '1.1rem' }}>Compétences Techniques</h3>
          </div>
          
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
            Modifiez ou ajoutez des compétences pour affiner votre matching IA.
          </p>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '2rem' }}>
            {profile.extracted_skills.map((skill) => (
              <span 
                key={skill} 
                style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '0.4rem', 
                  padding: '0.3rem 0.7rem', 
                  background: 'rgba(99, 102, 241, 0.1)', 
                  border: '1px solid rgba(99, 102, 241, 0.2)', 
                  borderRadius: '6px',
                  fontSize: '0.8rem',
                  color: 'var(--primary)',
                  fontWeight: 600
                }}
              >
                {skill}
                <X 
                  size={14} 
                  style={{ cursor: 'pointer', opacity: 0.7 }} 
                  onClick={() => removeSkill(skill)}
                />
              </span>
            ))}
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input 
              type="text" 
              placeholder="Ajouter (ex: Docker)"
              className="glass"
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && addSkill()}
              style={{ flex: 1, padding: '0.5rem 0.75rem', borderRadius: 'var(--radius-sm)', color: 'white', border: '1px solid var(--card-border)', outline: 'none', fontSize: '0.85rem' }}
            />
            <button 
              onClick={addSkill}
              className="btn glass" 
              style={{ padding: '0.5rem', width: '40px' }}
            >
              +
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

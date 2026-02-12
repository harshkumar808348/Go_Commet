import { useState } from 'react'
import Leaderboard from './components/Leaderboard'
import RankLookup from './components/RankLookup'
import SubmitScore from './components/SubmitScore'
import './App.css'

/**
 * Root application component.
 * Renders the leaderboard header, live top-10 table, and rank lookup panel.
 */
function App() {
  const [activeTab, setActiveTab] = useState('leaderboard')

  return (
    <div className="min-h-screen px-4 py-8 flex flex-col items-center">
      {/* ── Header ─────────────────────────────────────────── */}
      <header className="text-center mb-8 animate-fade-in">
        <h1 className="text-4xl font-bold tracking-tight mb-2 text-white">
          Gaming Leaderboard
        </h1>
        <p className="text-muted text-lg">
          Real-time global rankings
        </p>
      </header>

      {/* ── Tab Navigation ─────────────────────────────────── */}
      <nav className="flex bg-[var(--bg-card)] p-1 rounded-lg border border-[var(--border)] mb-8">
        <button
          onClick={() => setActiveTab('leaderboard')}
          className={`btn flex-1 ${activeTab === 'leaderboard' ? 'bg-[var(--bg-hover)] text-white shadow-sm' : 'text-muted hover:text-white'}`}
        >
          Leaderboard
        </button>
        <button
          onClick={() => setActiveTab('rank')}
          className={`btn flex-1 ${activeTab === 'rank' ? 'bg-[var(--bg-hover)] text-white shadow-sm' : 'text-muted hover:text-white'}`}
        >
          Rank Lookup
        </button>
        <button
          onClick={() => setActiveTab('submit')}
          className={`btn flex-1 ${activeTab === 'submit' ? 'bg-[var(--bg-hover)] text-white shadow-sm' : 'text-muted hover:text-white'}`}
        >
          Submit Score
        </button>
      </nav>

      {/* ── Content ────────────────────────────────────────── */}
      <main className="w-full max-w-2xl">
        {activeTab === 'leaderboard' && <Leaderboard />}
        {activeTab === 'rank' && <RankLookup />}
        {activeTab === 'submit' && <SubmitScore />}
      </main>

      {/* ── Footer ─────────────────────────────────────────── */}
      <footer className="mt-12 text-[var(--text-muted)] text-xs opacity-60">
        Gaming Leaderboard System &middot; FastAPI + React
      </footer>
    </div>
  )
}

export default App

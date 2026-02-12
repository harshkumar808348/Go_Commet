import { useState, useEffect, useCallback } from 'react'

const API_URL = 'http://localhost:8000/api/leaderboard'

/** Medal emoji for ranks 1–3. */
const MEDAL = { 1: '🥇', 2: '🥈', 3: '🥉' }

/** Accent colour per rank tier. */
const RANK_COLOR = {
    1: 'var(--accent-gold)',
    2: 'var(--accent-silver)',
    3: 'var(--accent-bronze)',
}

/**
 * Live-updating Top-10 Leaderboard.
 * Auto-refreshes every 5 seconds.
 */
export default function Leaderboard() {
    const [entries, setEntries] = useState([])
    const [updatedAt, setUpdatedAt] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [countdown, setCountdown] = useState(5)

    /** Fetch leaderboard data from the API. */
    const fetchLeaderboard = useCallback(async () => {
        try {
            const res = await fetch(`${API_URL}/top`)
            if (!res.ok) throw new Error(`HTTP ${res.status}`)
            const data = await res.json()
            setEntries(data.leaderboard || [])
            setUpdatedAt(new Date(data.updated_at))
            setError(null)
        } catch (err) {
            setError('Unable to load leaderboard')
            console.error('Leaderboard fetch error:', err)
        } finally {
            setLoading(false)
        }
    }, [])

    // Poll every 5 seconds
    useEffect(() => {
        fetchLeaderboard()
        const interval = setInterval(() => {
            fetchLeaderboard()
            setCountdown(5)
        }, 5000)
        return () => clearInterval(interval)
    }, [fetchLeaderboard])

    // Countdown timer
    useEffect(() => {
        const tick = setInterval(() => {
            setCountdown((c) => (c > 0 ? c - 1 : 5))
        }, 1000)
        return () => clearInterval(tick)
    }, [])

    // ── Render ──────────────────────────────────────────────────

    if (loading) {
        return (
            <div className="card p-12 text-center text-muted animate-fade-in">
                Loading...
            </div>
        )
    }

    if (error) {
        return (
            <div className="card p-8 text-center animate-fade-in border-red-900/50">
                <p className="text-red-400 mb-4">{error}</p>
                <button onClick={() => { setLoading(true); fetchLeaderboard() }} className="btn btn-primary">
                    Retry
                </button>
            </div>
        )
    }

    return (
        <div className="card p-0 overflow-hidden animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-[var(--border)] bg-[var(--bg-hover)]">
                <h2 className="font-semibold text-white">Top Players</h2>
                <span className="text-xs text-muted flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                    Update in {countdown}s
                </span>
            </div>

            {entries.length === 0 ? (
                <p className="text-center text-muted py-8">No scores yet.</p>
            ) : (
                <div className="divide-y divide-[var(--border)]">
                    {entries.map((entry, idx) => (
                        <div key={entry.user_id} className="flex items-center gap-4 px-4 py-3 hover:bg-[var(--bg-primary)] transition-colors">
                            {/* Rank */}
                            <div className={`w-8 h-8 flex items-center justify-center rounded font-bold text-sm ${idx < 3 ? 'text-yellow-400' : 'text-muted'}`}>
                                {idx + 1}
                            </div>

                            {/* Info */}
                            <div className="flex-1 min-w-0">
                                <p className="font-medium text-white truncate">{entry.username}</p>
                                <p className="text-xs text-muted">User {entry.user_id}</p>
                            </div>

                            {/* Score */}
                            <p className="font-mono font-medium text-white">
                                {entry.total_score.toLocaleString()}
                            </p>
                        </div>
                    ))}
                </div>
            )}

            {updatedAt && (
                <div className="p-2 text-center border-t border-[var(--border)] bg-[var(--bg-primary)]">
                    <p className="text-[10px] text-muted">Last sync: {updatedAt.toLocaleTimeString()}</p>
                </div>
            )}
        </div>
    )
}

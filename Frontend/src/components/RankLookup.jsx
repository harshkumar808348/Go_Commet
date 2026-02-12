import { useState } from 'react'

const API_URL = 'http://localhost:8000/api/leaderboard'

/**
 * Player Rank Lookup panel.
 * Enter a User ID to view their rank and total score.
 */
export default function RankLookup() {
    const [userId, setUserId] = useState('')
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    /** Query the rank endpoint for the entered user ID. */
    const handleSearch = async (e) => {
        e.preventDefault()
        const id = parseInt(userId, 10)
        if (!id || id <= 0) {
            setError('Please enter a valid positive User ID')
            return
        }

        setLoading(true)
        setError(null)
        setResult(null)

        try {
            const res = await fetch(`${API_URL}/rank/${id}`)
            if (res.status === 404) {
                setError('Player not found or has no leaderboard entry')
                return
            }
            if (!res.ok) throw new Error(`HTTP ${res.status}`)
            const data = await res.json()
            setResult(data)
        } catch (err) {
            setError('Failed to fetch rank. Is the server running?')
            console.error('Rank lookup error:', err)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="card p-6 animate-fade-in">
            <h2 className="font-bold text-white mb-6">Player Rank Lookup</h2>

            {/* Search form */}
            <form onSubmit={handleSearch} className="flex gap-2 mb-8">
                <input
                    type="number"
                    min="1"
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    placeholder="User ID (e.g. 101)"
                    className="flex-1 px-3 py-2 rounded bg-[var(--bg-primary)] border border-[var(--border)]
                     text-white placeholder-[var(--text-secondary)] outline-none
                     focus:border-[var(--accent)] transition-colors"
                />
                <button
                    type="submit"
                    disabled={loading}
                    className="btn btn-primary"
                >
                    {loading ? '...' : 'Search'}
                </button>
            </form>

            {/* Error */}
            {error && (
                <div className="p-3 mb-6 bg-red-900/20 border border-red-900/50 rounded text-red-300 text-sm text-center">
                    {error}
                </div>
            )}

            {/* Result card */}
            {result && (
                <div className="bg-[var(--bg-hover)] rounded-lg p-6 text-center border border-[var(--border)]">
                    <div className="text-4xl font-bold text-white mb-2">#{result.rank}</div>
                    <h3 className="text-lg font-medium text-[var(--text-secondary)] mb-6">{result.username}</h3>

                    <div className="grid grid-cols-2 gap-4 border-t border-[var(--border)] pt-4">
                        <div>
                            <p className="text-2xl font-bold text-white tabular-nums">
                                {result.total_score.toLocaleString()}
                            </p>
                            <p className="text-xs text-muted">Total Score</p>
                        </div>
                        <div>
                            <p className="text-2xl font-bold text-[var(--accent)] tabular-nums">
                                #{result.rank}
                            </p>
                            <p className="text-xs text-muted">Global Rank</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Empty state */}
            {!result && !error && !loading && (
                <p className="text-center text-muted text-sm py-8">
                    Enter a User ID to see their current standing.
                </p>
            )}
        </div>
    )
}

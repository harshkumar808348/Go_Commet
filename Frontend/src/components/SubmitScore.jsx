import { useState } from 'react'

const API_URL = 'http://localhost:8000/api/leaderboard'

export default function SubmitScore() {
    const [userId, setUserId] = useState('')
    const [score, setScore] = useState('')
    const [gameMode, setGameMode] = useState('solo')
    const [loading, setLoading] = useState(false)
    const [message, setMessage] = useState(null)
    const [error, setError] = useState(null)

    const handleSubmit = async (e) => {
        e.preventDefault()
        const uid = parseInt(userId, 10)
        const pts = parseInt(score, 10)

        if (!uid || uid <= 0) {
            setError('Invalid User ID')
            return
        }
        if (isNaN(pts) || pts <= 0) {
            setError('Score must be a positive number')
            return
        }

        setLoading(true)
        setError(null)
        setMessage(null)

        try {
            const res = await fetch(`${API_URL}/submit`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: uid,
                    score: pts,
                    game_mode: gameMode
                })
            })

            const data = await res.json()

            if (!res.ok) {
                // Handle 429 Rate Limit
                if (res.status === 429) {
                    throw new Error('Rate limit exceeded! You are submitting too fast.')
                }
                throw new Error(data.detail || `HTTP ${res.status}`)
            }

            setMessage(`Success! User ${data.user_id} is now Rank #${data.new_rank} (Total: ${data.new_total_score})`)
            setScore('') // Clear score to prevent double submit
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="card p-6 animate-fade-in">
            <h2 className="font-bold text-white mb-6">Submit New Score</h2>

            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <div>
                    <label className="block text-xs text-muted mb-1">User ID</label>
                    <input
                        type="number"
                        min="1"
                        required
                        value={userId}
                        onChange={(e) => setUserId(e.target.value)}
                        placeholder="e.g. 101"
                        className="w-full px-3 py-2 rounded bg-[var(--bg-primary)] border border-[var(--border)]
                         text-white outline-none focus:border-[var(--accent)] transition-colors"
                    />
                </div>

                <div>
                    <label className="block text-xs text-muted mb-1">Score</label>
                    <input
                        type="number"
                        min="1"
                        required
                        value={score}
                        onChange={(e) => setScore(e.target.value)}
                        placeholder="e.g. 500"
                        className="w-full px-3 py-2 rounded bg-[var(--bg-primary)] border border-[var(--border)]
                         text-white outline-none focus:border-[var(--accent)] transition-colors"
                    />
                </div>

                <div>
                    <label className="block text-xs text-muted mb-1">Game Mode</label>
                    <select
                        value={gameMode}
                        onChange={(e) => setGameMode(e.target.value)}
                        className="w-full px-3 py-2 rounded bg-[var(--bg-primary)] border border-[var(--border)]
                         text-white outline-none focus:border-[var(--accent)] transition-colors"
                    >
                        <option value="solo">Solo</option>
                        <option value="duo">Duo</option>
                        <option value="squad">Squad</option>
                        <option value="ranked">Ranked</option>
                    </select>
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="btn btn-primary mt-2"
                >
                    {loading ? 'Submitting...' : 'Submit Score'}
                </button>
            </form>

            {/* Error Message */}
            {error && (
                <div className="mt-6 p-3 bg-red-900/20 border border-red-900/50 rounded text-red-300 text-sm text-center animate-fade-in">
                    {error}
                </div>
            )}

            {/* Success Message */}
            {message && (
                <div className="mt-6 p-3 bg-green-900/20 border border-green-900/50 rounded text-green-300 text-sm text-center animate-fade-in">
                    {message}
                </div>
            )}
        </div>
    )
}

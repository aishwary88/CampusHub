import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { AxiosError } from 'axios'
import authService from '../../services/authService'

export default function Onboarding() {
  const [branch, setBranch] = useState('')
  const [year, setYear] = useState('1')
  const [password, setPassword] = useState('')
  const [bio, setBio] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      // 1. Update Profile (Branch, Year, Bio)
      await authService.updateProfile({
        branch,
        year: parseInt(year),
        bio
      })

      // 2. Set Backup Password if provided
      if (password.trim().length > 0) {
        if (password.length < 8) {
          setError('Backup password must be at least 8 characters long.')
          setLoading(false)
          return
        }
        await authService.setPassword({ password })
      }

      // 3. Success -> Navigate to home
      navigate('/')
    } catch (err) {
      const axiosErr = err as AxiosError<{ detail?: string }>
      setError(axiosErr.response?.data?.detail ?? 'Onboarding setup failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 px-4 py-12 relative overflow-hidden select-none font-sans">
      
      {/* Background blobs */}
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] rounded-full bg-indigo-600/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] rounded-full bg-blue-600/10 blur-[120px] pointer-events-none" />

      {/* Main Glassmorphic Card */}
      <div className="w-full max-w-md bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 rounded-2xl p-8 shadow-2xl transition duration-500 hover:border-slate-700/50">
        
        {/* Title */}
        <div className="text-center mb-8">
          <h2 className="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-100 to-indigo-200 tracking-tight">
            Complete Your Profile
          </h2>
          <p className="text-slate-400 text-xs mt-1.5 font-medium tracking-wide">
            Just a few more details to set up your CampusHub account.
          </p>
        </div>

        {/* Errors */}
        {error && (
          <div className="mb-5 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs font-medium flex items-center gap-3 animate-shake">
            <svg className="w-4 h-4 shrink-0 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          
          {/* Branch input */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">Branch / Department</label>
            <input
              type="text"
              required
              className="w-full bg-slate-950/40 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 transition duration-300"
              placeholder="e.g. Computer Science Engineering"
              value={branch}
              onChange={e => setBranch(e.target.value)}
            />
          </div>

          {/* Year dropdown */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">Academic Year</label>
            <select
              className="w-full bg-slate-950/40 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 transition duration-300"
              value={year}
              onChange={e => setYear(e.target.value)}
            >
              <option value="1">1st Year</option>
              <option value="2">2nd Year</option>
              <option value="3">3rd Year</option>
              <option value="4">4th Year</option>
            </select>
          </div>

          {/* Bio input */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">Bio (Optional)</label>
            <textarea
              className="w-full bg-slate-950/40 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 transition duration-300 resize-none h-20"
              placeholder="Tell us a bit about yourself..."
              value={bio}
              onChange={e => setBio(e.target.value)}
            />
          </div>

          {/* Backup password */}
          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-400">
                Backup Password (Optional)
              </label>
              <span className="text-[10px] text-slate-500 font-medium">For email login</span>
            </div>
            <input
              type="password"
              className="w-full bg-slate-950/40 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 transition duration-300"
              placeholder="Min. 8 characters"
              value={password}
              onChange={e => setPassword(e.target.value)}
            />
            <p className="text-[10px] text-slate-500 mt-1.5 leading-relaxed">
              Highly recommended: Set a password to log in directly if Google authentication is ever offline.
            </p>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-3 px-4 rounded-xl shadow-lg shadow-indigo-600/20 hover:shadow-indigo-500/30 transition duration-300 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed text-sm mt-6"
          >
            {loading ? (
              <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            ) : (
              <span>Complete Setup</span>
            )}
          </button>
        </form>

      </div>
    </div>
  )
}

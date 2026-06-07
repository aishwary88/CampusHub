import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import type { AxiosError } from 'axios'
import authService from '../../services/authService'

declare global {
  interface Window {
    google: any
  }
}

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  
  const navigate = useNavigate()
  const location = useLocation()
  
  // Google Client ID
  const GOOGLE_CLIENT_ID = (import.meta.env.VITE_GOOGLE_CLIENT_ID as string) || '1047120619890-dummy.apps.googleusercontent.com'

  useEffect(() => {
    // Check if redirecting from registration or login
    if (location.pathname === '/register') {
      setIsLogin(false)
    } else {
      setIsLogin(true)
    }
  }, [location.pathname])

  // Load Google Identity Services SDK
  useEffect(() => {
    const script = document.createElement('script')
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true
    document.body.appendChild(script)

    script.onload = () => {
      if (window.google) {
        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: handleGoogleCredential,
          auto_select: false,
          cancel_on_tap_outside: true,
        })
        
        window.google.accounts.id.renderButton(
          document.getElementById('google-signin-btn'),
          { 
            theme: 'filled_black', 
            size: 'large', 
            width: '380', 
            text: 'continue_with',
            shape: 'rectangular'
          }
        )
      }
    }

    return () => {
      document.body.removeChild(script)
    }
  }, [])

  const handleGoogleCredential = async (response: any) => {
    setError(null)
    setLoading(true)
    try {
      const res = await authService.googleLogin({
        credential_token: response.credential,
      })
      if (res.is_new_user) {
        navigate('/onboarding')
      } else {
        navigate('/')
      }
    } catch (err) {
      const axiosErr = err as AxiosError<{ detail?: string }>
      setError(axiosErr.response?.data?.detail ?? 'Google authentication failed')
    } finally {
      setLoading(false)
    }
  }

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    
    // Validate domain before sending to backend
    const parts = email.split('@')
    if (parts.length === 2) {
      const domain = parts[1].toLowerCase()
      if (domain !== 'mitsgwl.ac.in' && domain !== 'mitsgwalior.in') {
        setError('Only @mitsgwl.ac.in and @mitsgwalior.in email domains are allowed.')
        setLoading(false)
        return
      }
    } else {
      setError('Please enter a valid email address.')
      setLoading(false)
      return
    }

    try {
      if (isLogin) {
        await authService.login({ email, password })
        navigate('/')
      } else {
        await authService.register({ name, email, password })
        setError(null)
        // Switch to login mode on success
        setIsLogin(true)
        alert('Registration successful! Please login with your credentials.')
      }
    } catch (err) {
      const axiosErr = err as AxiosError<{ detail?: string }>
      setError(axiosErr.response?.data?.detail ?? `${isLogin ? 'Login' : 'Registration'} failed`)
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
        
        {/* Logo and Tagline */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center p-3 rounded-2xl bg-gradient-to-tr from-indigo-500 to-blue-500 shadow-lg mb-3">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-100 to-indigo-200 tracking-tight">
            CampusHub
          </h1>
          <p className="text-slate-400 text-sm mt-1.5 font-medium tracking-wide">
            Connect • Learn • Grow
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

        {/* Google Authentication Button */}
        <div className="mb-6 flex flex-col items-center justify-center">
          <div id="google-signin-btn" className="w-full flex justify-center py-0.5 rounded-lg overflow-hidden border border-slate-700/50 hover:border-slate-500/50 transition duration-300 bg-black min-h-[44px]" />
        </div>

        {/* OR Divider */}
        <div className="relative flex items-center my-6">
          <div className="flex-grow border-t border-slate-800/80"></div>
          <span className="flex-shrink mx-4 text-xs font-semibold uppercase tracking-wider text-slate-500">OR</span>
          <div className="flex-grow border-t border-slate-800/80"></div>
        </div>

        {/* Email + Password Form */}
        <form onSubmit={handleEmailSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">Full Name</label>
              <input
                type="text"
                required
                className="w-full bg-slate-950/40 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 transition duration-300"
                placeholder="John Doe"
                value={name}
                onChange={e => setName(e.target.value)}
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">College Email</label>
            <input
              type="email"
              required
              className="w-full bg-slate-950/40 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 transition duration-300"
              placeholder="username@mitsgwl.ac.in"
              value={email}
              onChange={e => setEmail(e.target.value)}
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-400">Password</label>
              {isLogin && (
                <span className="text-xs text-indigo-400 hover:text-indigo-300 cursor-pointer font-medium transition duration-200">
                  Forgot Password?
                </span>
              )}
            </div>
            <input
              type="password"
              required
              className="w-full bg-slate-950/40 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 transition duration-300"
              placeholder="••••••••"
              value={password}
              onChange={e => setPassword(e.target.value)}
            />
          </div>

          {/* Form Submit Button */}
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
              <span>{isLogin ? 'Sign In' : 'Create Account'}</span>
            )}
          </button>
        </form>

        {/* Toggle Mode Footer */}
        <div className="text-center mt-6">
          <p className="text-xs text-slate-500">
            {isLogin ? "Don't have an account? " : 'Already have an account? '}
            <span
              onClick={() => setIsLogin(!isLogin)}
              className="text-indigo-400 hover:text-indigo-300 font-semibold cursor-pointer transition duration-200"
            >
              {isLogin ? 'Sign Up' : 'Sign In'}
            </span>
          </p>
        </div>

        {/* Premium Informational Footer */}
        <div className="mt-8 pt-6 border-t border-slate-800/80 text-center">
          <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-2.5">
            Strictly Allowed MITS Domains
          </p>
          <div className="flex justify-center items-center gap-2">
            <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-bold uppercase tracking-wider">
              Student: @mitsgwl.ac.in
            </span>
            <span className="px-2.5 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[10px] font-bold uppercase tracking-wider">
              Faculty: @mitsgwalior.in
            </span>
          </div>
        </div>

      </div>
    </div>
  )
}

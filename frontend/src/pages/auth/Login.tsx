import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { AxiosError } from 'axios'
import authService from '../../services/authService'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    try {
      await authService.login({ email, password })
      navigate('/')
    } catch (err) {
      const axiosErr = err as AxiosError<{ detail?: string }>
      setError(axiosErr.response?.data?.detail ?? 'Login failed')
    }
  }

  return (
    <form onSubmit={submit} className="max-w-md mx-auto bg-white p-6 rounded shadow">
      <h2 className="text-xl mb-4">Login</h2>

      {error && (
        <div role="alert" className="mb-4 rounded bg-red-100 px-4 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      <label className="block mb-2">
        <span>Email</span>
        <input
          type="email"
          className="mt-1 block w-full"
          value={email}
          onChange={e => setEmail(e.target.value)}
        />
      </label>
      <label className="block mb-2">
        <span>Password</span>
        <input
          type="password"
          className="mt-1 block w-full"
          value={password}
          onChange={e => setPassword(e.target.value)}
        />
      </label>
      <button className="mt-4 bg-blue-600 text-white px-4 py-2 rounded">Login</button>
    </form>
  )
}

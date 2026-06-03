import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import authService from '../../services/authService'
import type { AxiosError } from 'axios'

export default function Register() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    try {
      await authService.register({ name, email, password })
      navigate('/login')
    } catch (err) {
      const axiosErr = err as AxiosError<{ detail?: string }>
      setError(axiosErr.response?.data?.detail ?? 'Registration failed')
    }
  }

  return (
    <form onSubmit={submit} className="max-w-md mx-auto bg-white p-6 rounded shadow">
      <h2 className="text-xl mb-4">Register</h2>
      <label className="block mb-2">
        <span>Name</span>
        <input
          type="text"
          className="mt-1 block w-full"
          value={name}
          onChange={e => setName(e.target.value)}
        />
      </label>
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
      {error && (
        <div className="mt-2 text-red-600 text-sm" role="alert">
          {error}
        </div>
      )}
      <button className="mt-4 bg-green-600 text-white px-4 py-2 rounded">Register</button>
    </form>
  )
}

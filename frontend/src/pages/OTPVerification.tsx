import React, { useState } from 'react'
import authService from '../services/authService'

export default function OTPVerification(){
  const [email, setEmail] = useState('')
  const [otp, setOtp] = useState('')

  const submit = async (e: React.FormEvent) =>{
    e.preventDefault()
    try{
      await authService.verifyOtp({email, otp})
      alert('Verified')
    }catch(err){
      alert('Verification failed')
    }
  }

  return (
    <form onSubmit={submit} className="max-w-md mx-auto bg-white p-6 rounded shadow">
      <h2 className="text-xl mb-4">OTP Verification</h2>
      <label className="block mb-2">
        <span>Email</span>
        <input className="mt-1 block w-full" value={email} onChange={e=>setEmail(e.target.value)} />
      </label>
      <label className="block mb-2">
        <span>OTP</span>
        <input className="mt-1 block w-full" value={otp} onChange={e=>setOtp(e.target.value)} />
      </label>
      <button className="mt-4 bg-indigo-600 text-white px-4 py-2 rounded">Verify</button>
    </form>
  )
}

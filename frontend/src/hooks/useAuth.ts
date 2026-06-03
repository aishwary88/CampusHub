import { useState, useEffect } from 'react'

export default function useAuth(){
  const [token, setToken] = useState<string | null>(null)
  useEffect(()=>{
    setToken(localStorage.getItem('access_token'))
  },[])
  const logout = ()=>{
    localStorage.removeItem('access_token')
    setToken(null)
  }
  return { token, logout }
}

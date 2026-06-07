import axios from 'axios'

// Use relative base URL so requests go through Vite's proxy → no CORS issues
const API_BASE = import.meta.env.VITE_API_BASE || ''

const api = axios.create({
  baseURL: API_BASE,
})

api.interceptors.request.use((config)=>{
  const token = localStorage.getItem('access_token')
  if(token && config.headers){
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api

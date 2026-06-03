import api from './api'
import type { User, RegisterPayload, LoginPayload, Token } from '../types/index.d'

export const register = (payload: RegisterPayload): Promise<User> =>
  api.post<User>('/api/auth/register', payload).then((res) => res.data)

export const login = async (payload: LoginPayload): Promise<Token> => {
  const res = await api.post<Token>('/api/auth/login', payload)
  localStorage.setItem('access_token', res.data.access_token)
  return res.data
}

export const getMe = (): Promise<User> =>
  api
    .get<User>('/api/auth/me', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
    })
    .then((res) => res.data)

// verifyOtp is retained for OTPVerification.tsx (future sprint feature)
export const verifyOtp = (payload: { email: string; otp: string }): Promise<unknown> =>
  api.post('/api/auth/otp/verify', payload).then((res) => res.data)

export default { register, login, getMe, verifyOtp }

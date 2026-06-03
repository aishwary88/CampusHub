export interface User {
  id: number
  name: string | null
  email: string
  role: 'STUDENT' | 'FACULTY' | 'ADMIN'
  branch: string | null
  year: number | null
  profile_photo: string | null
  bio: string | null
  campus_score: number
  is_verified: boolean
  created_at: string
  updated_at: string | null
}

export interface RegisterPayload {
  name?: string
  email: string
  password: string
}

export interface LoginPayload {
  email: string
  password: string
}

export interface Token {
  access_token: string
  token_type: string
}

export interface User {
  id: number
  name: string | null
  email: string
  role: 'STUDENT' | 'FACULTY' | 'ADMIN'
  branch: string | null
  year: number | null
  profile_photo: string | null
  bio: string | null
  google_id: string | null
  auth_provider: 'GOOGLE' | 'EMAIL' | 'BOTH'
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

export interface GoogleLoginResponse {
  access_token: string
  token_type: string
  is_new_user: boolean
}

export interface SetPasswordPayload {
  password: string
}

export interface UpdateProfilePayload {
  name?: string
  branch?: string
  year?: number
  bio?: string
}


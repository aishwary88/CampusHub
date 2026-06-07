import React from 'react'
import { Routes, Route } from 'react-router-dom'
import AuthPage from '../pages/auth/AuthPage'
import Onboarding from '../pages/auth/Onboarding'
import OTPVerification from '../pages/OTPVerification'
import Home from '../pages/Home'
import MainLayout from '../layouts/MainLayout'
import AuthLayout from '../layouts/AuthLayout'
import PrivateRoute from './PrivateRoute'

export default function AppRoutes() {
  return (
    <Routes>
      {/* Public routes with AuthLayout */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<AuthPage />} />
        <Route path="/register" element={<AuthPage />} />
        <Route path="/otp" element={<OTPVerification />} />
      </Route>

      {/* Protected routes with PrivateRoute */}
      <Route element={<PrivateRoute />}>
        <Route path="/onboarding" element={<Onboarding />} />
        <Route element={<MainLayout />}>
          <Route path="/" element={<Home />} />
        </Route>
      </Route>
    </Routes>
  )
}


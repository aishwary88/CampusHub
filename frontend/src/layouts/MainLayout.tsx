import React from 'react'
import { Outlet } from 'react-router-dom'

export default function MainLayout() {
  return (
    <div>
      <header className="p-4 bg-white shadow">CampusHub</header>
      <div className="p-4">
        <Outlet />
      </div>
    </div>
  )
}

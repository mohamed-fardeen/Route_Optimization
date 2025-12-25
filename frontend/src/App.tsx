import React from 'react'
import Dashboard from './pages/Dashboard'

export default function App(){
  return (
    <div className="app-root">
      <header className="app-header">
        <div className="brand">RouteOptimizer</div>
        <div className="sub">Dashboard</div>
      </header>
      <main className="app-main">
        <Dashboard />
      </main>
      <footer className="app-footer">© {new Date().getFullYear()} RouteOptimizer</footer>
    </div>
  )
}

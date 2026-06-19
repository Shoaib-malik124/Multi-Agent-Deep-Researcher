import React, { useState } from 'react'
import { NavLink } from 'react-router-dom'

function NavigationBar() {
  const [isOpen, setIsOpen] = useState(false)

  const closeMenu = () => setIsOpen(false)

  const linkClasses = ({ isActive }) =>
    `relative px-1 py-2 text-sm font-medium transition-colors duration-200 ${
      isActive
        ? 'text-white after:absolute after:left-0 after:-bottom-1 after:h-0.5 after:w-full after:rounded-full after:bg-indigo-500'
        : 'text-slate-300 hover:text-white'
    }`

  return (
    <nav className="sticky top-0 z-50 flex items-center justify-between bg-slate-900 px-8 py-3 shadow-lg shadow-black/20">

      <div className="flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500 font-bold text-white">
          R
        </div>
        <p className="text-lg font-bold tracking-wide text-white">
          Researcher
        </p>
      </div>

      <div className="absolute left-1/2 hidden -translate-x-1/2 items-center gap-8 md:flex">
        <NavLink to="/" className={linkClasses}>
          Dashboard
        </NavLink>
        <NavLink to="/documents" className={linkClasses}>
          Documents
        </NavLink>
      </div>

      <div className="flex min-w-[100px] items-center justify-end gap-3">
        <button className="rounded-lg px-4 py-1.5 text-sm font-medium text-slate-300 transition-colors hover:text-white">
          Log in
        </button>
        <button className="rounded-lg bg-indigo-500 px-4 py-1.5 text-sm font-medium text-white shadow-sm transition-colors hover:bg-indigo-400">
          Sign up
        </button>
      </div>

    </nav>
  )
}

export default NavigationBar
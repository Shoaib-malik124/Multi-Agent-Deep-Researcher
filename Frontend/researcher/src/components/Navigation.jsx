import React, { useState } from 'react'
import { NavLink } from 'react-router-dom'

import { useAuth, useClerk,UserButton,useUser } from "@clerk/clerk-react";
import Register from './Login';

function NavigationBar() {
  const {openSignIn}=useClerk()
  const {user}=useUser()
  const {getToken}=useAuth() // will be used later to get the jwt for backend calls.

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
        {
          user ? (
            <div className="flex items-center gap-8">
              <NavLink to="/" className={linkClasses} >
                Dashboard
              </NavLink>
              <NavLink to={`/documents`} className={linkClasses}>
                Documents
              </NavLink>
            </div>
          ) : (
            <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-amber-400" />
              <p className="text-sm text-slate-300">
                You're not signed in —{' '}
                <button className="font-medium text-indigo-400 hover:text-indigo-300"
                  onClick={openSignIn}
                >
                  sign in to continue
                </button>
              </p>
            </div>
          )
        }
      </div>

      <div className="flex min-w-[100px] items-center justify-end gap-3">
        {
          user?<div className="flex items-center gap-3">
              <p className="max-sm:hidden text-white">Hi, {user.firstName+" "+user.lastName}</p>
              <UserButton/>
          </div>:
          <div className="flex gap-4 max-sm:text-xs">
              <Register/>
          </div>
        }
      </div>

    </nav>
  )
}

export default NavigationBar
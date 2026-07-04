import React, { useState } from 'react'
import { NavLink } from 'react-router-dom'

import { useAuth, useClerk,UserButton,useUser } from "@clerk/clerk-react";
import Register from './Login';

function NavigationBar() {
  const {openSignIn}=useClerk()
  const {user}=useUser()
  const {getToken}=useAuth() // will be used later to get the jwt for backend calls.
  const [showDropDown,setShowDropDown]=useState(false)

  const linkClasses = ({ isActive }) =>
    `relative px-1 py-2 text-sm font-medium transition-colors duration-200 ${
      isActive
        ? 'text-white after:absolute after:left-0 after:-bottom-1 after:h-0.5 after:w-full after:rounded-full after:bg-indigo-500'
        : 'text-slate-300 hover:text-white'
    }`

  return (
    <nav className="sticky top-0 z-50 flex items-center justify-between bg-slate-900 px-8 py-3 shadow-lg shadow-black/20">

      <div className="flex items-center gap-2">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-indigo-500 text-white">
        R
      </div>

      <p className="truncate text-base font-bold text-white">
        Researcher
      </p>
    </div>

      <div className="absolute left-1/2 hidden -translate-x-1/2 items-center gap-8 md:flex">
        {
          // This automatically gets removed for small screens,so place a hamburger.
          user ? (
            <div className="flex items-center gap-8">
              <NavLink to="/" className={linkClasses} >
                Dashboard
              </NavLink>
              <NavLink to="/documents" className={linkClasses}>
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

      {/* For small screens */}
      <div className="ml:auto md:hidden">
        {
          showDropDown ? (
            <div className="absolute right-3 top-full mt-2 w-44 rounded-xl border border-white/10 bg-[#1c1d3a] p-2 shadow-2xl shadow-black/40">
            {
              user ? (
                <div className="flex flex-col gap-1">
                  
                  <div className="flex items-center gap-2 sm:gap-3">
                    <UserButton />
                  </div>

                  <NavLink
                    to="/"
                    className={linkClasses}
                    onClick={() => setShowDropDown(false)}
                  >
                    Dashboard
                  </NavLink>

                  <NavLink
                    to="/documents"
                    className={linkClasses}
                    onClick={() => setShowDropDown(false)}
                  >
                    Documents
                  </NavLink>

                </div>
              ) : (
                <div className="flex flex-col items-stretch p-1">
                  <Register />
                </div>
              )
            }
            </div>
          ) : 
          (
            <div>
              <button 
               onClick={() => setShowDropDown(true)}
               aria-label="Open menu"
               className="flex h-9 w-9 items-center justify-center rounded-lg border border-white/10 bg-white/5 text-white transition-colors hover:bg-white/10 active:scale-95"
               >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          )
        }
      </div>

      <div className="hidden md:flex min-w-[60px] items-center justify-end gap-2 sm:min-w-[100px] sm:gap-3">
        {
          user ? (
            <div className="flex items-center gap-2 sm:gap-3">
              <p className="hidden text-sm text-white sm:block sm:text-base">
                Hi, {user.firstName + " " + user.lastName}
              </p>
              <UserButton />
            </div>
          ) : (
            <div className="flex gap-2 sm:gap-4">
              <Register />
            </div>
          )
        }
      </div>

    </nav>
  )
}

export default NavigationBar
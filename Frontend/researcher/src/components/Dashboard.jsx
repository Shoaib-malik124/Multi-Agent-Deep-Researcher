import React, { useState } from 'react'
import { useUser } from '@clerk/clerk-react'
import Dashbackground from './Dashbackground.jsx'

function Dashboard() {
  const { user } = useUser()
  const [query, setQuery] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    // API Call later
  }

  return (
    <main className="relative flex min-h-[calc(100vh-64px)] items-center justify-center overflow-hidden bg-slate-50 px-4 py-10 sm:px-6 sm:py-16">

      <Dashbackground />

      <div className="relative w-full max-w-xl rounded-2xl border border-slate-200 bg-white p-5 shadow-xl shadow-slate-200/50 sm:p-8">

        <h1 className="mb-1 text-xl font-bold text-slate-900 sm:text-2xl">
          Start Your Research
        </h1>
        <p className="mb-5 text-sm text-slate-500 sm:mb-6">
          Describe Your Research Area Topic.
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-2">
          <label htmlFor="query-taker" className="text-sm font-medium text-slate-700">
            Enter Your Research Topic
          </label>
          <textarea
            id="query-taker"
            placeholder={
              user ? "Describe your research topic" : "Login/Signup to continue"
            }
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            rows={4}
            className="w-full resize-none rounded-lg border border-slate-300 px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 sm:px-4 sm:py-3 sm:rows-5"
          />
          <button
            type="submit"
            className="mt-2 w-full rounded-lg bg-indigo-500 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition-colors hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto sm:self-end sm:py-2"
            disabled={!query.trim() || !user}
          >
            Upload query
          </button>
        </form>

      </div>
    </main>
  )
}

export default Dashboard
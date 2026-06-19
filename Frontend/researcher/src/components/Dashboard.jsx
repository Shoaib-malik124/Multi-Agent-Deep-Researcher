import React, { useState } from 'react'
import Dashbackground from './Dashbackground';

function Dashboard() {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // API Call later
    setQuery("");
  }

  return (
    <main className="relative flex min-h-[calc(100vh-64px)] items-center justify-center overflow-hidden bg-slate-50 px-4 py-16">

      <Dashbackground/>

      <div className="relative w-full max-w-xl rounded-2xl border border-slate-200 bg-white p-8 shadow-xl shadow-slate-200/50">

        <h1 className="mb-1 text-2xl font-bold text-slate-900">
          Start Your Research
        </h1>
        <p className="mb-6 text-sm text-slate-500">
          Describe Your Research Area Topic.
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-2">
          <label htmlFor="query-taker" className="text-sm font-medium text-slate-700">
            Enter Your Research Topic
          </label>
          <textarea
            id="query-taker"
            placeholder="Enter a concise and detailed query about your research topic"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            rows={5}
            className="w-full resize-none rounded-lg border border-slate-300 px-4 py-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
          />
          <button
            type="submit"
            className="mt-2 self-end rounded-lg bg-indigo-500 px-5 py-2 text-sm font-medium text-white shadow-sm transition-colors hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={!query.trim()}
          >
            Upload query
          </button>
        </form>

      </div>
    </main>
  )
}

export default Dashboard
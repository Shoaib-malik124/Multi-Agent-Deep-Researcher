import React from 'react'
import { useUser } from '@clerk/clerk-react'
import Dashbackground from './Dashbackground.jsx'

function Documents() {
  const { user } = useUser()

  return (
    <main className="relative flex min-h-[calc(100vh-64px)] items-center justify-center overflow-hidden bg-slate-50 px-4 py-16">

      <Dashbackground />

      <div className="relative w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-xl shadow-slate-200/50">

        <div className="mx-auto mb-5 flex h-12 w-12 items-center justify-center rounded-full bg-indigo-50">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6 text-indigo-500"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.8}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>

        <h1 className="mb-1 text-xl font-bold text-slate-900">
          Your document is ready
        </h1>
        <p className="mb-6 text-sm text-slate-500">
          "We've finished generating your research document. Download it below."
        </p>

        <button
          className="w-full rounded-lg bg-indigo-500 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition-colors hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Download
        </button>

      </div>
    </main>
  )
}

export default Documents
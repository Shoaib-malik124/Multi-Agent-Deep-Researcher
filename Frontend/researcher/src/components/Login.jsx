import React from 'react'
import { useClerk } from "@clerk/clerk-react";

function Register() {
  const { openSignIn } = useClerk()

  return (
    <button
      onClick={openSignIn}
      className="rounded-full bg-blue-600 px-4 py-1.5 text-xs font-medium text-white transition-colors hover:bg-blue-500 active:scale-95 sm:px-6 sm:py-2 sm:text-sm"
    >
      Register
    </button>
  )
}

export default Register
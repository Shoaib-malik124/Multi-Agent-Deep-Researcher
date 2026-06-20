import React from 'react'
import { useClerk } from "@clerk/clerk-react";

function Register() {
  const {openSignIn}=useClerk()

  return (
    <button onClick={openSignIn} className="bg-blue-600 text-white px-6 sm:px-9 py-2 rounded-full">Register</button>
  )
}

export default Register
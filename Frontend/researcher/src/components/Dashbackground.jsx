import React from 'react'

function Dashbackground() {
  return (
      <>
        {/* Neural network mesh background */}
        <svg
        className="pointer-events-none absolute inset-0 h-full w-full opacity-[0.07]"
        preserveAspectRatio="xMidYMid slice"
        viewBox="0 0 1200 800"
        >
            <g stroke="#1a1a2e" strokeWidth="1" fill="none">
            <line x1="100" y1="120" x2="280" y2="200" />
            <line x1="280" y1="200" x2="480" y2="100" />
            <line x1="480" y1="100" x2="680" y2="220" />
            <line x1="680" y1="220" x2="900" y2="140" />
            <line x1="280" y1="200" x2="220" y2="380" />
            <line x1="480" y1="100" x2="440" y2="340" />
            <line x1="680" y1="220" x2="640" y2="400" />
            <line x1="900" y1="140" x2="950" y2="360" />
            <line x1="220" y1="380" x2="440" y2="340" />
            <line x1="440" y1="340" x2="640" y2="400" />
            <line x1="640" y1="400" x2="950" y2="360" />
            <line x1="220" y1="380" x2="160" y2="580" />
            <line x1="440" y1="340" x2="400" y2="600" />
            <line x1="640" y1="400" x2="680" y2="620" />
            <line x1="950" y1="360" x2="980" y2="600" />
            <line x1="160" y1="580" x2="400" y2="600" />
            <line x1="400" y1="600" x2="680" y2="620" />
            <line x1="680" y1="620" x2="980" y2="600" />
            <line x1="100" y1="120" x2="60" y2="340" />
            <line x1="900" y1="140" x2="1080" y2="280" />
            <line x1="1080" y1="280" x2="980" y2="600" />
            </g>
            <g fill="#1a1a2e">
            <circle cx="100" cy="120" r="5" />
            <circle cx="280" cy="200" r="5" />
            <circle cx="480" cy="100" r="5" />
            <circle cx="680" cy="220" r="5" />
            <circle cx="900" cy="140" r="5" />
            <circle cx="220" cy="380" r="5" />
            <circle cx="440" cy="340" r="5" />
            <circle cx="640" cy="400" r="5" />
            <circle cx="950" cy="360" r="5" />
            <circle cx="160" cy="580" r="5" />
            <circle cx="400" cy="600" r="5" />
            <circle cx="680" cy="620" r="5" />
            <circle cx="980" cy="600" r="5" />
            <circle cx="60" cy="340" r="5" />
            <circle cx="1080" cy="280" r="5" />
            </g>
        </svg>
      </> 
  )
}

export default Dashbackground
import { useState } from 'react'

import NavigationBar from './components/Navigation.jsx'
import {BrowserRouter, Route, Routes} from 'react-router-dom'
import Dashboard from './components/Dashboard.jsx'
import Documents from './components/Documents.jsx'

function App() {
  
  return (
    <>
      <BrowserRouter>
         <NavigationBar/>
         <Routes>
            <Route path='/' element={<Dashboard/>}/>
            <Route path='/documents' element={<Documents/>}/>
         </Routes>
      </BrowserRouter>
    </>
  )
}

export default App

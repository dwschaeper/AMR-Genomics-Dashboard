import { useEffect, useState } from "react"
import Plot from "react-plotly.js"
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'

import Overview from './components/Overview.jsx'
import AMR from './components/AMR.jsx'
import AddIsolate from './components/AddIsolate.jsx'
import './App.css'

function App() {
  return (
    <>
    <BrowserRouter>
      <div className='hero'>
        <h1>Antimicrobial Resistance Dashboard</h1>
          <nav>
            <Link to="/">Overview</Link>
            <Link to="/amr">AMR</Link>
            <Link to='/add'>Add Isolate</Link>
          </nav>
      </div>

      <div style={{alignItems: "center", textAlign: "center"}}>
        <h2>Explore genomic surveillance data include isolate metadata, genome assemblies, and AMR gene annotations.</h2>
      </div>

      <div>
          <Routes>
            <Route path='/' element={<Overview />} />
            <Route path='/amr' element={<AMR />} />
            <Route path='/add' element={<AddIsolate />} />
          </Routes>
      </div>

    </BrowserRouter>
    </>
  )
}

export default App;
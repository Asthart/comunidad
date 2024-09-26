import React from 'react'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'
import Inicio from './components/Inicio'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Inicio />} />
        {/* Aquí agregarías otras rutas en el futuro */}
      </Routes>
    </Router>
  )
}

export default App
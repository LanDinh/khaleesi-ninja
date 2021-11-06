import React, { ReactElement } from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import './App.css'


/**
 * Renders the gate.
 * @return { ReactElement }
 * @constructor
 */
function Gate() {
  return (
    <React.StrictMode><BrowserRouter><Routes>
      <Route path="/" element={<div>Test</div>} />
    </Routes></BrowserRouter></React.StrictMode>
  )
}

export default Gate

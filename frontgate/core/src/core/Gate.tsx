// React.
import React, { ReactElement } from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'

// khaleesi.ninja.
import { SayHelloRequest } from './proto/core_backgate_pb'
import { GateKeeperClient }   from './proto/core_backgate_grpc_web_pb'
import './App.css'


/**
 * Renders the gate.
 * @return { ReactElement }
 * @constructor
 */
function Gate() {
  const service = new GateKeeperClient('https://core.development.khaleesi.ninja')
  const request = new SayHelloRequest()
  request.setName('Khaleesi, Mother of Dragons')
  service.sayHello(request, {}, ((_err, response) => console.log(response)))

  return (
    <React.StrictMode><BrowserRouter><Routes>
      <Route path="/" element={<div>Test</div>} />
    </Routes></BrowserRouter></React.StrictMode>
  )
}

export default Gate

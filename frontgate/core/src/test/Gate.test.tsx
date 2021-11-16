// React.
import React              from 'react'
import { render, screen } from '@testing-library/react'

// khaleesi.ninja.
import Gate              from '../core/Gate'
import { ServiceClient } from '../core/proto/core_backgate_grpc_web_pb'


jest.mock('../core/proto/core_backgate_grpc_web_pb')

beforeEach(() => {
  (ServiceClient as jest.Mock).mockClear()
})


test('renders learn react link', () => {
  render(<Gate />)

  expect(ServiceClient).toHaveBeenCalledTimes(1)
  const mockServiceClient = (ServiceClient as jest.Mock).mock.instances[0]
  const mockSayHello = mockServiceClient.sayHello
  expect(mockSayHello).toHaveBeenCalledTimes(1)

  const linkElement = screen.getByText(/Test/i)
  expect(linkElement).toBeInTheDocument()
})

import '@testing-library/jest-dom'
import type { ActionFunctionArgs } from '@remix-run/node'
import { render, screen } from '@testing-library/react'
import * as nodeMock from '@remix-run/node'
import { LoginRoute, action } from '../../app/khaleesi/auth/login'
import { createTestingStub } from '../util/remixStub'


jest.mock('@remix-run/node', () => ({
  json: jest.fn(),
}))
const sessionMock = jest.fn()
jest.mock('../../app/khaleesi/auth/session.server', () => ({
  Session: jest.fn(() => ({
    init  : jest.fn(),
    create: sessionMock,
  }))
}))


const buildActionArguments = (user: string | Blob): ActionFunctionArgs => {
  const formData = new FormData()
  if ('string' === typeof user) {
    formData.append('user', user)
  } else {
    formData.append('user', user, 'filename')
  }
  return {
    request: new Request('http:example.com', { method: 'POST', body: formData }),
    params : {},
    context: {},
  }
}


test('Rendering the login form.', () => {
  // Prepare data.
  let RemixStub = createTestingStub(LoginRoute)
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(screen.getByRole('button', { name: 'Login' })).toBeInTheDocument()
})

test('Logging in with invalid user type.', async () => {
  // Prepare data.
  const jsonSpy = jest.spyOn(nodeMock, 'json')
  // Execute test.
  await action(buildActionArguments(new Blob()))
  // Assert result.
  expect(sessionMock).not.toHaveBeenCalled()
  expect(jsonSpy).toHaveBeenCalled()
})

test('Logging in.', async () => {
  // Execute test.
  await action(buildActionArguments('user'))
  // Assert result.
  expect(sessionMock).toHaveBeenCalled()
})

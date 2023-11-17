import '@testing-library/jest-dom'
import type { ActionFunctionArgs } from '@remix-run/node'
import { render, screen } from '@testing-library/react'
import * as sessionMock from '../../app/khaleesi/auth/session'
import * as nodeMock from '@remix-run/node'
import { LoginRoute, action } from '../../app/khaleesi/auth/login'
import { createTestingStub } from '../util/remixStub'


jest.mock('../../app/khaleesi/auth/session', () => ({
  createUserSession: jest.fn(),
  getSessionData: jest.fn(() => Promise.resolve({ json: jest.fn(() => ({ session: jest.fn() })) })),
  destroySession: jest.fn(),
}))
jest.mock('@remix-run/node', () => ({
  json: jest.fn(),
  redirect: jest.fn(),
}))


const buildActionArguments = (action: string, user?: Blob): ActionFunctionArgs => {
  const formData = new FormData()
  formData.append('action', action)
  if (user) {
    formData.append('user', user, 'filename')
  } else {
    formData.append('user', 'user')
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
  const createUserSessionSpy = jest.spyOn(sessionMock, 'createUserSession')
  const jsonSpy               = jest.spyOn(nodeMock   , 'json')
  // Execute test.
  await action(buildActionArguments('login', new Blob()))
  // Assert result.
  expect(createUserSessionSpy).not.toHaveBeenCalled()
  expect(jsonSpy).toHaveBeenCalled()
})

test('Logging in.', async () => {
  // Prepare data.
  const createUserSessionSpy = jest.spyOn(sessionMock, 'createUserSession')
  // Execute test.
  await action(buildActionArguments('login'))
  // Assert result.
  expect(createUserSessionSpy).toHaveBeenCalled()
})

test('Logging out.', async () => {
  // Prepare data.
  const destroySessionSpy = jest.spyOn(sessionMock, 'destroySession')
  const redirectSpy      = jest.spyOn(nodeMock   , 'redirect')
  // Execute test.
  await action(buildActionArguments('logout'))
  // Assert result.
  expect(destroySessionSpy).toHaveBeenCalled()
  expect(redirectSpy).toHaveBeenCalled()
})

test('Unknown action.', async () => {
  // Prepare data.
  const jsonSpy = jest.spyOn(nodeMock, 'json')
  // Execute test.
  await action(buildActionArguments('unknown'))
  // Assert result.
  expect(jsonSpy).toHaveBeenCalled()
})

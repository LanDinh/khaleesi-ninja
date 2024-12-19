import '@testing-library/jest-dom'
import type { ActionFunctionArgs } from '@remix-run/node'
import { render, screen } from '@testing-library/react'
import { LoginRoute, action } from '../../app/khaleesi/auth/login'
import { suppressReactRouterFutureWarnings } from '../../app/khaleesi/testUtil/consoleLogging'
import { createTestingStub } from '../../app/khaleesi/testUtil/remixStub'


jest.mock('@remix-run/node', () => ({
  json: jest.fn(),
}))
const originalWarning = console.warn.bind(console.warn)

const sessionMock = jest.fn()
jest.mock('../../app/khaleesi/auth/session.server', () => ({
  Session: jest.fn(() => ({
    init  : jest.fn(),
    create: sessionMock,
  })),
}))

beforeAll(() => {
  console.warn = suppressReactRouterFutureWarnings(originalWarning)
})
afterAll(() => {
  console.warn = originalWarning
  jest.clearAllMocks()
})


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
  const RemixStub = createTestingStub(LoginRoute)
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(screen.getByRole('button', { name: 'Login' })).toBeInTheDocument()
})

/*

TODO(51): figure out why this test times out on request.formData()

test('Logging in with invalid user type.', async () => {
  // Prepare data.
  const jsonSpy = jest.spyOn(global.Response, 'json')
  // Execute test.
  await action(buildActionArguments(new Blob()))
  // Assert result.
  expect(sessionMock).not.toHaveBeenCalled()
  expect(jsonSpy).toHaveBeenCalled()
})*/

test('Logging in.', async () => {
  // Execute test.
  await action(buildActionArguments('user'))
  // Assert result.
  expect(sessionMock).toHaveBeenCalled()
})

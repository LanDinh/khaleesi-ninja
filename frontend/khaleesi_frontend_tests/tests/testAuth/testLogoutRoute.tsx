import '@testing-library/jest-dom'
import type { ActionFunctionArgs } from '@remix-run/node'
import { render, screen } from '@testing-library/react'
import LogoutRoute, { action } from '../../app/khaleesi/auth/logoutRoute'
import { suppressReactRouterFutureWarnings } from '../../app/khaleesi/testUtil/consoleLogging'
import { createTestingStub } from '../../app/khaleesi/testUtil/remixStub'


const originalWarning = console.warn.bind(console.warn)

jest.mock('@remix-run/node', () => ({
  json: jest.fn(),
}))
const sessionMock = jest.fn()
jest.mock('../../app/khaleesi/auth/session.server', () => ({
  Session: jest.fn(() => ({
    init  : jest.fn(),
    destroy: sessionMock,
  }))
}))

beforeAll(() => {
  console.warn = suppressReactRouterFutureWarnings(originalWarning)
})
afterAll(() => {
  console.warn = originalWarning
  jest.clearAllMocks()
})


const buildActionArguments = (): ActionFunctionArgs => {
  return {
    request: new Request('http:example.com', { method: 'POST' }),
    params : {},
    context: {},
  }
}


test('Rendering the logout form.', () => {
  // Prepare data.
  const RemixStub = createTestingStub(LogoutRoute)
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(screen.getByRole('button', { name: 'Logout' })).toBeInTheDocument()
})

test('Logging out.', async () => {
  // Execute test.
  await action(buildActionArguments())
  // Assert result.
  expect(sessionMock).toHaveBeenCalled()
})

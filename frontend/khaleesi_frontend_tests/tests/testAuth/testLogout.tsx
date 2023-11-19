import '@testing-library/jest-dom'
import type { ActionFunctionArgs } from '@remix-run/node'
import { render, screen } from '@testing-library/react'
import { LogoutRoute, action } from '../../app/khaleesi/auth/logout'
import { createTestingStub } from '../util/remixStub'


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


const buildActionArguments = (): ActionFunctionArgs => {
  return {
    request: new Request('http:example.com', { method: 'POST' }),
    params : {},
    context: {},
  }
}


test('Rendering the logout form.', () => {
  // Prepare data.
  let RemixStub = createTestingStub(LogoutRoute)
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

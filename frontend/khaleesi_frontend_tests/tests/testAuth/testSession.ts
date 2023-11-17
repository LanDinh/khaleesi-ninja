import '@testing-library/jest-dom'
import { createUserSession, getSessionData } from '../../app/khaleesi/auth/session'


// Need to mock everything instead of using jest.requireActual because of errors...
jest.mock('@remix-run/node', () => ({
  createCookieSessionStorage: jest.fn(() => ({
    getSession    : jest.fn(() => ({
      set: jest.fn(),
      has: jest.fn((permission) => 'permission' === permission),
      get: jest.fn(() => 'permission'),
    })),
    commitSession : jest.fn(),
    destroySession: jest.fn(),
  })),
  redirect: jest.fn(),
  json: jest.fn((json) => ({ json: jest.fn(() => json) })),
}))


test('Creating user session.', async () => {
  // Execute test.
  await createUserSession('session', '/redirect')
})

test('Getting session data with permission.', async () => {
  // Execute test.
  const result =
    await getSessionData(new Request('http://example.com'), 'permission')
    .then((response) => response.json())
  // Assert result.
  expect(result.permission).toBe(true)
})

test('Getting session data without permission.', async () => {
  // Execute test.
  const result =
    await getSessionData(new Request('http://example.com'))
    .then((response) => response.json())
  // Assert result.
  expect(result.permission).toBe(false)
})

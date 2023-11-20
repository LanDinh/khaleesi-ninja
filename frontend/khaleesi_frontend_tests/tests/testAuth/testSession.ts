import '@testing-library/jest-dom'
import * as nodeMock from '@remix-run/node'
import { Session } from '../../app/khaleesi/auth/session.server'


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
  redirectDocument: jest.fn(),
  redirect: jest.fn(),
  json: jest.fn((json) => ({ json: jest.fn(() => json) })),
}))


const REMIX_SESSION_MOCK = {
  id: '',
  data: {},
  has: (): boolean => true,
  get: (): undefined => 'permission' as unknown as undefined,
  set: (): void => {},
  flash: (): void => {},
  unset: (): void => {},
}


describe('hasPermission', () => {
  test('Check permission if none is required.', () => {
    // Prepare data.
    const session = new Session()
    // Execute test.
    const result = session.hasPermission()
    // Assert result.
    expect(result).toBe(true)
  })

  test('Check permission if session isn\'t initialized yet.', () => {
    // Prepare data.
    const session = new Session()
    session.initialized = false
    // Execute test.
    const result = session.hasPermission('permission')
    // Assert result.
    expect(result).toBe(false)
  })

  test('Check permission if user isn\'t authenticated.', () => {
    // Prepare data.
    const session = new Session()
    session.initialized = true
    // Execute test.
    const result = session.hasPermission('anonymous')
    // Assert result.
    expect(result).toBe(true)
  })

  test('Check permission if user has no permissions.', () => {
    // Prepare data.
    const session = new Session()
    session.initialized = true
    session.remixSession = { ...REMIX_SESSION_MOCK, has: (): boolean => false }
    // Execute test.
    const result = session.hasPermission('permission')
    // Assert result.
    expect(result).toBe(false)
  })

  test('Check permission if user has permission.', () => {
    // Prepare data.
    const session = new Session()
    session.initialized = true
    session.remixSession = { ...REMIX_SESSION_MOCK, has: (): boolean => true }
    // Execute test.
    const result = session.hasPermission('permission')
    // Assert result.
    expect(result).toBe(false)
  })
})

describe('requirePermission', () => {
  test('Check permission if none is required.', () => {
    // Prepare data.
    const session = new Session()
    // Execute test & assert result.
    expect(() => session.requirePermission()).not.toThrow()
  })

  test('Check permission if session isn\'t initialized yet.', () => {
    // Prepare data.
    const session = new Session()
    session.initialized = false
    // Execute test & assert result.
    expect(() => session.requirePermission('permission')).toThrow()
  })

  test('Check permission if user isn\'t authenticated.', () => {
    // Prepare data.
    const session = new Session()
    session.initialized = true
    // Execute test & assert result.
    expect(() => session.requirePermission('permission')).toThrow()
  })

  test('Check permission if user has no permissions.', () => {
    // Prepare data.
    const session = new Session()
    session.initialized = true
    session.remixSession = { ...REMIX_SESSION_MOCK, has: (): boolean => false }
    // Execute test & assert result.
    expect(() => session.requirePermission('permission')).toThrow()
  })

  test('Check permission if user has permission.', () => {
    // Prepare data.
    const session = new Session()
    session.initialized = true
    session.authenticated = true
    session.remixSession = { ...REMIX_SESSION_MOCK, has: (): boolean => true }
    // Execute test & assert result.
    expect(() => session.requirePermission('permission')).not.toThrow()
  })
})

test('Initialize user session.', async () => {
  // Prepare data.
  const session = new Session()
  expect(session.remixSession).toBeFalsy()
  // Execute test.
  await session.init(new Request('http:example.com', { method: 'POST' }))
  // Assert result.
  expect(session.remixSession).toBeTruthy()
  expect(session.initialized).toBe(true)
  expect(session.authenticated).toBe(true)
})

test('Create user session without initializing.', async () => {
  // Prepare data.
  const session = new Session()
  const jsonSpy = jest.spyOn(nodeMock, 'json')
  // Execute test.
  await session.create('id', 'redirect')
  // Assert result.
  expect(jsonSpy).toHaveBeenCalled()
})

test('Create user session.', async () => {
  // Prepare data.
  const session = new Session()
  session.initialized = true
  session.remixSession = { ...REMIX_SESSION_MOCK }
  const redirectSpy = jest.spyOn(nodeMock, 'redirectDocument')
  // Execute test.
  await session.create('id', 'redirect')
  // Assert result.
  expect(redirectSpy).toHaveBeenCalled()
})

test('Destroy user session.', async () => {
  // Prepare data.
  const session = new Session()
  session.initialized = true
  session.remixSession = { ...REMIX_SESSION_MOCK }
  const redirectSpy = jest.spyOn(nodeMock, 'redirectDocument')
  // Execute test.
  await session.destroy('redirect')
  // Assert result.
  expect(redirectSpy).toHaveBeenCalled()
  expect(session.initialized).toBe(false)
  expect(session.authenticated).toBe(false)
})

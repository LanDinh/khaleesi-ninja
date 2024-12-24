import '@testing-library/jest-dom'
import { loader } from '../../app/khaleesi/home/document.server'


jest.mock('@remix-run/node')

const hasPermissionMock = jest.fn()
jest.mock('../../app/khaleesi/auth/session.server', () => ({
  Session: jest.fn(() => ({
    init         : jest.fn(),
    hasPermission: hasPermissionMock,
  }))
}))

afterAll(() => {
  jest.clearAllMocks()
})


test('Navigation data gets filtered according to permissions.', async () => {
  // Prepare data.
  // Execute test.
  await loader({ request: new Request('http://example.com'), params: {}, context: {} })
  // Assert result.
  expect(hasPermissionMock).toHaveBeenCalledTimes(3)
})

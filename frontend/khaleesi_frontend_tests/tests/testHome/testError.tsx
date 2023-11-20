import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import * as hooks from '@remix-run/react'
import { ErrorPage } from '../../app/khaleesi/home/error'
import { createTestingStub } from '../util/remixStub'


jest.mock('@remix-run/react', () => ({
  ...jest.requireActual('@remix-run/react'),
  useRouteError: jest.fn(),
  isRouteErrorResponse: jest.fn(),
}))

afterAll(() => {
  jest.clearAllMocks()
})


test('ErrorPage renders route errors.', (): void => {
  // Prepare data.
  jest.spyOn(hooks, 'isRouteErrorResponse').mockReturnValue(true)
  jest.spyOn(hooks, 'useRouteError').mockReturnValue({ status: 1337, data: { message: 'FooBar' } })
  let RemixStub = createTestingStub(ErrorPage)
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(screen.queryByText('Woops!', { exact: false })).toBeNull()
  expect(screen.queryByText('again', { exact: false })).toBeNull()
  expect(screen.getByText('HTTP 1337')).toBeInTheDocument()
  expect(screen.getByText('FooBar')).toBeInTheDocument()
})

test('ErrorPage renders unknown errors.', (): void => {
  // Prepare data.
  jest.spyOn(hooks, 'isRouteErrorResponse').mockReturnValue(false)
  jest.spyOn(hooks, 'useRouteError').mockReturnValue(Error('message'))
  let RemixStub = createTestingStub(ErrorPage)
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(screen.getByText('Woops!', { exact: false })).toBeInTheDocument()
  expect(screen.queryByText('again', { exact: false })).toBeNull()
  expect(screen.getByText('message', { exact: false })).toBeInTheDocument()
})

test('ErrorPage renders unknown non-errors.', (): void => {
  // Prepare data.
  jest.spyOn(hooks, 'isRouteErrorResponse').mockReturnValue(false)
  jest.spyOn(hooks, 'useRouteError').mockReturnValue({ message: 'message' })
  let RemixStub = createTestingStub(ErrorPage)
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(screen.getByText('Woops!', { exact: false })).toBeInTheDocument()
  expect(screen.getByText('again', { exact: false })).toBeInTheDocument()
  expect(screen.queryByText('message', { exact: false })).toBeNull()
})

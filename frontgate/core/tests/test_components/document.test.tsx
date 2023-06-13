import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { App, ErrorBoundary, links } from '../../app/khaleesi/components/document'
import { suppressConsoleFunction } from '../util/consoleLogging'
import { createRemixStub } from '../util/remixStub'
import { ErrorPage } from '../../app/khaleesi/components/error'


jest.mock('../../app/khaleesi/components/error')


const originalError = console.error.bind(console.error)

beforeAll(() => {
  window.scrollTo = jest.fn()
  console.error = suppressConsoleFunction('validateDOMNesting', originalError)
})
afterAll(() => {
  console.error = originalError
  jest.clearAllMocks()
})

test('App gets rendered without errors.', () => {
  // Prepare data.
  let RemixStub = createRemixStub(<App />, 'TEST')
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(screen.getByText('TEST')).toBeInTheDocument()
})

test('ErrorBoundary gets rendered without errors.', () => {
  // Prepare data.
  const mockErrorPage = ErrorPage as jest.MockedFunction<typeof ErrorPage>
  mockErrorPage.mockImplementation(() => <></>)
  let RemixStub = createRemixStub(<ErrorBoundary />)
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(mockErrorPage).toHaveBeenCalled()
})

test('links contain all links.', () => {
  // Execute test & assert result.
  expect(links().length).toBe(2)
})

import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { App, ErrorBoundary, links } from '../../../app/khaleesi/components/document'
import { ErrorPage } from '../../../app/khaleesi/components/error'
import { NavigationBar } from '../../../app/khaleesi/components/navigation/navigationBar'
import { suppressConsoleFunction } from '../../util/consoleLogging'
import { createRemixStub } from '../../util/remixStub'


jest.mock('../../../app/khaleesi/components/error')
jest.mock('../../../app/khaleesi/components/navigation/navigationBar')


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
  const mockNavigationBar = NavigationBar as jest.MockedFunction<typeof NavigationBar>
  mockNavigationBar.mockImplementation(() => <></>)
  let RemixStub = createRemixStub(<App />, 'TEST')
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(screen.getByText('TEST')).toBeInTheDocument()
  expect(mockNavigationBar).toHaveBeenCalled()
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
  // Font, rootStyles, navigationBarStyles.
  expect(links().length).toBe(3)
})
import '@testing-library/jest-dom'
import { render } from '@testing-library/react'
import { App, ErrorBoundary, links } from '../../app/khaleesi/components/document'
import { Navigation } from '../../app/khaleesi/navigation/navigation'
import { Content } from '../../app/khaleesi/components/content'
import { suppressConsoleFunction } from '../util/consoleLogging'
import { createTestingStub } from '../util/remixStub'


const originalError = console.error.bind(console.error)
jest.mock('../../app/khaleesi/components/navigation/navigation')
jest.mock('../../app/khaleesi/components/content')

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
  const mockNavigationBar = Navigation as jest.MockedFunction<typeof Navigation>
  mockNavigationBar.mockImplementation(() => <></>)
  const mockContent = Content as jest.MockedFunction<typeof  Content>
  mockContent.mockImplementation(() => <></>)
  let RemixStub = createTestingStub(() => <App title="Test App" />)
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(mockNavigationBar).toHaveBeenCalled()
  expect(mockContent).toHaveBeenCalled()
})

test('ErrorBoundary gets rendered without errors.', () => {
  // Prepare data.
  const mockNavigationBar = Navigation as jest.MockedFunction<typeof Navigation>
  mockNavigationBar.mockImplementation(() => <></>)
  const mockContent = Content as jest.MockedFunction<typeof  Content>
  mockContent.mockImplementation(() => <></>)
  let RemixStub = createTestingStub(() => <ErrorBoundary title="Test App" />)
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(mockNavigationBar).toHaveBeenCalled()
  expect(mockContent).toHaveBeenCalled()
})

test('links contain all links.', () => {
  // Execute test & assert result.
  // Font, rootStyles, navigationBarStyles.
  expect(links().length).toBe(3)
})

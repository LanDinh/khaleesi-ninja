import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { App, ErrorBoundary, links } from '../../app/khaleesi/components/document'
import { suppressConsoleFunction } from '../util/consoleLogging'
import { createRemixStub } from '../util/remixStub'


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
  let RemixStub = createRemixStub(<App />, 'TEST')
  render(<RemixStub />)
  expect(screen.getByText('TEST')).toBeInTheDocument()
})

test('ErrorBoundary gets rendered without errors.', () => {
  let RemixStub = createRemixStub(<ErrorBoundary />)
  render(<RemixStub />)
  expect(screen.getByText('Woops!', { exact: false })).toBeInTheDocument()
})

test('links contain all links.', () => {
  expect(links().length).toBe(2)
})

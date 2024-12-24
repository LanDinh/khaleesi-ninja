import '@testing-library/jest-dom'
import { render } from '@testing-library/react'
import * as reactMock from 'react-router'
import { App, ErrorBoundary, links } from '../../app/khaleesi/home/document'
import { Navigation } from '../../app/khaleesi/navigation/navigation'
import { BreadCrumbs } from '../../app/khaleesi/navigation/breadcrumb'
import { Content } from '../../app/khaleesi/home/content'
import {
  suppressConsoleFunction,
  suppressReactRouterFutureWarnings,
} from '../../app/khaleesi/testUtil/consoleLogging'
import { createTestingStub } from '../../app/khaleesi/testUtil/remixStub'


const originalError = console.error.bind(console.error)
const originalWarning = console.warn.bind(console.warn)

jest.mock('../../app/khaleesi/navigation/navigation')
jest.mock('../../app/khaleesi/home/content')
jest.mock('../../app/khaleesi/navigation/breadcrumb')
jest.mock('@remix-run/node')
jest.mock('react-router', () => ({
  ...jest.requireActual('react-router'),
  useLoaderData: jest.fn(),
}))

const hasPermissionMock = jest.fn()
jest.mock('../../app/khaleesi/auth/session.server', () => ({
  Session: jest.fn(() => ({
    init         : jest.fn(),
    hasPermission: hasPermissionMock,
  }))
}))

beforeAll(() => {
  window.scrollTo = jest.fn()
  console.error = suppressConsoleFunction(['validateDOMNesting'], originalError)
  console.warn = suppressReactRouterFutureWarnings(originalWarning)
})
afterAll(() => {
  console.error = originalError
  console.warn = originalWarning
  jest.clearAllMocks()
})


test('App gets rendered without errors.', () => {
  // Prepare data.
  jest.spyOn(reactMock, 'useLoaderData').mockReturnValue({ top: [], middle: [], bottom: [] })
  const mockNavigationBar = Navigation as jest.MockedFunction<typeof Navigation>
  mockNavigationBar.mockImplementation(() => <></>)
  const mockContent = Content as jest.MockedFunction<typeof  Content>
  mockContent.mockImplementation(() => <></>)
  const mockBreadCrumbs = BreadCrumbs as jest.MockedFunction<typeof BreadCrumbs>
  mockBreadCrumbs.mockImplementation(() => <></>)
  const RemixStub = createTestingStub(() => <App title="Test App" />)
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(mockNavigationBar).toHaveBeenCalled()
  expect(mockContent).toHaveBeenCalled()
  expect(mockBreadCrumbs).toHaveBeenCalled()
})

test('ErrorBoundary gets rendered without errors.', () => {
  // Prepare data.
  const mockNavigationBar = Navigation as jest.MockedFunction<typeof Navigation>
  mockNavigationBar.mockImplementation(() => <></>)
  const mockContent = Content as jest.MockedFunction<typeof  Content>
  mockContent.mockImplementation(() => <></>)
  const mockBreadCrumbs = BreadCrumbs as jest.MockedFunction<typeof BreadCrumbs>
  mockBreadCrumbs.mockImplementation(() => <></>)
  const RemixStub = createTestingStub(() => <ErrorBoundary title="Test App" />)
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(mockNavigationBar).toHaveBeenCalled()
  expect(mockContent).toHaveBeenCalled()
  expect(mockBreadCrumbs).toHaveBeenCalled()
})

test('links contain all links.', () => {
  // Execute test & assert result.
  // Font, rootStyles, navigationStyles, tableStyles, chipStyles.
  expect(links().length).toBe(5)
})

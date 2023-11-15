import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import * as router from '@remix-run/react'
import { NavigationElement } from '../../../app/khaleesi/navigation/navigationElement'
import { breadcrumb, BreadCrumbs } from '../../../app/khaleesi/navigation/breadcrumb'


jest.mock('../../../app/khaleesi/components/navigation/navigationElement')
jest.mock('@remix-run/react', () => ({
  ...jest.requireActual('@remix-run/react'),
  useMatches: jest.fn(),
}))


test('BreadCrumbs render without errors.', () => {
  // Prepare data.
  const matchA = {
    id: 'test1',
    pathname: '',
    params  : {},
    data    : null,
    handle  : {
      breadcrumb: (): JSX.Element => <div>TEST1</div>
    }
  }
  const matchB = {
    id: 'test2',
    pathname: '',
    params  : {},
    data    : null,
    handle  : {
      breadcrumb: (): JSX.Element => <div>TEST2</div>
    }
  }
  jest.spyOn(router, 'useMatches').mockReturnValue([ matchA, matchB ])
  // Execute test.
  render(<BreadCrumbs />)
  // Assert result.
  expect(screen.getByText('TEST1')).toBeInTheDocument()
  expect(screen.getByText('TEST2')).toBeInTheDocument()
  expect(screen.getByText('>')).toBeInTheDocument()
})

test('Providing breadcrumb data works as expected.', () => {
  // Prepare data.
  const mockNavigationElement = NavigationElement as jest.MockedFunction<typeof NavigationElement>
  mockNavigationElement.mockImplementation(() => <></>)
  const navigationElementProperties = {
    path : '/test',
    label: 'TEST',
    icon: <div>Icon</div>,
  }
  // Execute test.
  render(breadcrumb(navigationElementProperties).breadcrumb())
  // Assert result.
  expect(mockNavigationElement).toHaveBeenCalled()
})

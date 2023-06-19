import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import * as router from '@remix-run/react'
import type {
  NavigationElementProperties,
} from '../../../../app/khaleesi/components/navigation/navigationElement'
import { NavigationElement } from '../../../../app/khaleesi/components/navigation/navigationElement'
import { breadcrumb, BreadCrumbs } from '../../../../app/khaleesi/components/navigation/breadcrumb'


jest.mock('../../../../app/khaleesi/components/navigation/navigationElement')
jest.mock('@remix-run/react', () => ({
  ...jest.requireActual('@remix-run/react'),
  useMatches: jest.fn(),
}))


test('BreadCrumbs render without errors.', () => {
  // Prepare data.
  const match = {
    id: 'test',
    pathname: '',
    params  : {},
    data    : null,
    handle  : {
      breadcrumb: (element: NavigationElementProperties): JSX.Element => <div>TEST</div>
    }
  }
  jest.spyOn(router, 'useMatches').mockReturnValue([match])
  // Execute test.
  render(<BreadCrumbs />)
  // Assert result.
  expect(screen.getByText('TEST')).toBeInTheDocument()
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
  const match = {
    id: 'test',
    pathname: '',
    params  : {},
    data    : null
  }
  // Execute test.
  render(breadcrumb(navigationElementProperties).breadcrumb(match))
  // Assert result.
  expect(mockNavigationElement).toHaveBeenCalled()
})

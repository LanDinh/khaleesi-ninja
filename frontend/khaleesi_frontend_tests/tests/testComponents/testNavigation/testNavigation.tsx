import '@testing-library/jest-dom'
import { render, screen, fireEvent } from '@testing-library/react'
import * as router from '@remix-run/react'
import { Navigation } from '../../../app/khaleesi/components/navigation/navigation'
import { MenuIcon } from '../../../app/khaleesi/components/icon'
import type {
  NavigationElementProperties,
} from '../../../app/khaleesi/components/navigation/navigationElement'
import {
  NavigationMenuElement,
} from '../../../app/khaleesi/components/navigation/navigationElement'
import { createTestingStub } from '../../util/remixStub'


jest.mock('../../../app/khaleesi/components/icon')
jest.mock('../../../app/khaleesi/components/navigation/navigationElement')
jest.mock('@remix-run/react', () => ({
  ...jest.requireActual('@remix-run/react'),
  useMatches: jest.fn(),
}))
jest.mock(
  '../../../app/navigationData',
  (): { navigationData: NavigationElementProperties[] } => ({
    navigationData: [
      {
        path: '/alpha',
        label: 'ALPHA',
        icon: <>a</>,
        children: [ { path: '/alpha/1', label: 'ONE', icon: <>1</> } ],
      },
      {
        path: '/beta',
        label: 'BETA',
        icon: <>b</>,
        children: [ { path: '/beta/2', label: 'TWO', icon: <>2</> } ],
      },
    ],
  }),
)

test('Navigation menu renders without errors.', () => {
  // Prepare data.
  // noinspection JSUnusedLocalSymbols
  const match = {
    id: 'test',
    pathname: '/alpha',
    params  : {},
    data    : null,
    handle  : {
      breadcrumb: (element: NavigationElementProperties): JSX.Element => <div>TEST</div>
    }
  }
  jest.spyOn(router, 'useMatches').mockReturnValue([ match ])
  const mockMenuIcon = MenuIcon as jest.MockedFunction<typeof MenuIcon>
  mockMenuIcon.mockImplementation(() => <></>)
  const mockElement = NavigationMenuElement as jest.MockedFunction<typeof NavigationMenuElement>
  mockElement.mockImplementation(() => <></>)
  let RemixStub = createTestingStub(Navigation, '/alpha')
  // Execute test.
  const result = render(<RemixStub initialEntries={['/alpha']}/>)
  // Assert result.
  expect(mockMenuIcon).toHaveBeenCalled()
  expect(mockElement).toBeCalledTimes(4)
  expect(result.container.querySelectorAll('details').length).toBe(3)
  expect(result.container.querySelectorAll('details')[1]).toHaveAttribute('open')
  expect(result.container.querySelectorAll('details')[2]).not.toHaveAttribute('open')
})

test('NavigationMenu closes when link is clicked.', () => {
  // Prepare data.
  jest.spyOn(router, 'useMatches').mockReturnValue([])
  const mockMenuIcon = MenuIcon as jest.MockedFunction<typeof MenuIcon>
  mockMenuIcon.mockImplementation(() => <></>)
  const mockElement = NavigationMenuElement as jest.MockedFunction<typeof NavigationMenuElement>
  mockElement.mockImplementation(({ onClick }) => <div onClick={onClick}>TEST</div>)
  let RemixStub = createTestingStub(Navigation, '/alpha')
  // Execute test.
  const result = render(<RemixStub initialEntries={['/alpha']}/>)
  fireEvent.click(screen.getAllByText('TEST')[0])
  // Assert result.
  expect(result.container.querySelectorAll('details')[0]).not.toHaveAttribute('open')
})

test('NavigationMenu closes when clicking outside the menu.', () => {
  // Prepare data.
  jest.spyOn(router, 'useMatches').mockReturnValue([])
  const mockMenuIcon = MenuIcon as jest.MockedFunction<typeof MenuIcon>
  mockMenuIcon.mockImplementation(() => <></>)
  const mockElement = NavigationMenuElement as jest.MockedFunction<typeof NavigationMenuElement>
  mockElement.mockImplementation(({ onClick }) => <div onClick={onClick}>TEST</div>)
  let RemixStub = createTestingStub(Navigation, '/alpha')
  // Execute test.
  const result = render(<RemixStub initialEntries={['/alpha']}/>)
  fireEvent.click(result.container.querySelector('#khaleesi-navigation-background')!)
  // Assert result.
  expect(result.container.querySelectorAll('details')[0]).not.toHaveAttribute('open')
})

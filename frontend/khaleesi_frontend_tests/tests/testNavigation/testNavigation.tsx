import '@testing-library/jest-dom'
import { render, screen, fireEvent } from '@testing-library/react'
import * as router from '@remix-run/react'
import { Navigation } from '../../app/khaleesi/navigation/navigation'
import { MenuIcon } from '../../app/khaleesi/home/icon'
import type {
  NavigationElementProperties,
} from '../../app/khaleesi/navigation/navigationElement'
import {
  NavigationMenuElement,
} from '../../app/khaleesi/navigation/navigationElement'
import { createTestingStub } from '../util/remixStub'


jest.mock('../../app/khaleesi/home/icon')
jest.mock('../../app/khaleesi/navigation/navigationElement')
jest.mock('@remix-run/react', () => ({
  ...jest.requireActual('@remix-run/react'),
  useMatches: jest.fn(),
}))


const navigationDataElement = (name: string): NavigationElementProperties => {
  return {
    path: '/' + name,
    label: name.toUpperCase(),
    icon: <div>{name}</div>
  }
}

const navigationData = (area: string): NavigationElementProperties[] => {
  const parent  = navigationDataElement('parent-' + area)
  const sibling = navigationDataElement('sibling-' + area)
  const child   = navigationDataElement('child-' + area)
  return [
    { ...parent, children: [{ ...child }] },
    { ...sibling },
  ]
}

test('Navigation menu renders without errors.', () => {
  // Prepare data.
  // noinspection JSUnusedLocalSymbols
  const match = {
    id: '/parent-top',
    pathname: '/parent-top',
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
  let RemixStub = createTestingStub(
    () => <Navigation
      top={navigationData('top')}
      middle={navigationData('middle')}
      bottom={navigationData('bottom')}
    />,
    '/parent-top/child-top',
    )
  // Execute test.
  const result = render(<RemixStub initialEntries={['/parent-top/child-top']}/>)
  // Assert result.
  expect(mockMenuIcon).toHaveBeenCalled()
  expect(mockElement).toBeCalledTimes(9)
  expect(result.container.querySelectorAll('details').length).toBe(4)
  expect(result.container.querySelectorAll('details')[1]).toHaveAttribute('open')
  expect(result.container.querySelectorAll('details')[2]).not.toHaveAttribute('open')
  expect(result.container.querySelectorAll('details')[3]).not.toHaveAttribute('open')
})

test('NavigationMenu closes when link is clicked.', () => {
  // Prepare data.
  jest.spyOn(router, 'useMatches').mockReturnValue([])
  const mockMenuIcon = MenuIcon as jest.MockedFunction<typeof MenuIcon>
  mockMenuIcon.mockImplementation(() => <></>)
  const mockElement = NavigationMenuElement as jest.MockedFunction<typeof NavigationMenuElement>
  mockElement.mockImplementation(({ onClick }) => <div onClick={onClick}>TEST</div>)
  let RemixStub = createTestingStub(
    () => <Navigation
      top={navigationData('top')}
      middle={navigationData('middle')}
      bottom={navigationData('bottom')}
    />,
    '/parent-top/child-top',
  )
  // Execute test.
  const result = render(<RemixStub initialEntries={['/parent-top/child-top']}/>)
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
  let RemixStub = createTestingStub(
    () => <Navigation
      top={navigationData('top')}
      middle={navigationData('middle')}
      bottom={navigationData('bottom')}
    />,
    '/parent-top/child-top',
  )
  // Execute test.
  const result = render(<RemixStub initialEntries={['/parent-top/child-top']}/>)
  fireEvent.click(result.container.querySelector('#khaleesi-navigation-background')!)
  // Assert result.
  expect(result.container.querySelectorAll('details')[0]).not.toHaveAttribute('open')
})

import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import {
  NavigationElement,
  NavigationMenuElement,
} from '../../app/khaleesi/navigation/navigationElement'
import { createTestingStub } from '../util/remixStub'


test('NavigationElement renders without error.', () => {
  // Prepare data.
  const navigationElementProperties = {
    path : '/test',
    label: 'TEST',
    icon: <div>Icon</div>,
  }
  let RemixStub = createTestingStub(
    () => <NavigationElement element={navigationElementProperties} />,
  )
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(screen.getByText('TEST', { exact: false })).toBeInTheDocument()
  expect(screen.getByText('Icon')).toBeInTheDocument()
})

test('NavigationMenuElement renders without error for common icon.', () => {
  // Prepare data.
  const navigationElementProperties = {
    path : '/home',
    label: 'Home',
    icon: <div>Icon</div>,
  }
  let RemixStub = createTestingStub(
    () => <NavigationMenuElement element={navigationElementProperties} onClick={(): void => {}} />,
  )
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(screen.getByText('Home', { exact: false })).toBeInTheDocument()
  expect(screen.queryByText('Icon missing!')).toBeNull()
})

test('NavigationMenuElement renders without error for app specific icon.', () => {
  // Prepare data.
  const navigationElementProperties = {
    path : '/test',
    label: 'Test',
    icon: <div>Icon</div>,
  }
  let RemixStub = createTestingStub(
    () => <NavigationMenuElement element={navigationElementProperties} onClick={(): void => {}} />,
  )
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(screen.getByText('Test Icon')).toBeInTheDocument()
  expect(screen.queryByText('Icon missing!')).toBeNull()
})

test('NavigationMenuElement renders without error for missing icon.', () => {
  // Prepare data.
  const navigationElementProperties = {
    path : '/missing',
    label: 'Missing Label',
    icon: <div>Icon</div>,
  }
  let RemixStub = createTestingStub(
    () => <NavigationMenuElement element={navigationElementProperties} onClick={(): void => {}} />,
  )
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(screen.getByText('Missing Label', { exact: false })).toBeInTheDocument()
  expect(screen.queryByText('Common')).toBeNull()
  expect(screen.queryByText('Specific')).toBeNull()
  expect(screen.queryByText('Icon')).toBeNull()
  expect(screen.getByText('Icon missing!')).toBeInTheDocument()
})

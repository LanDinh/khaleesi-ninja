import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import {
  NavigationElement,
  NavigationMenuElement,
} from '../../../app/khaleesi/components/navigation/navigationElement'
import { createRemixStub } from '../../util/remixStub'


test('NavigationElement renders without error.', () => {
  // Prepare data.
  const navigationElementProperties = {
    path : '/test',
    label: 'TEST',
    icon: <div>Icon</div>,
  }
  let RemixStub = createRemixStub(<NavigationElement element={navigationElementProperties} />)
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(screen.getByText('TEST', { exact: false })).toBeInTheDocument()
  expect(screen.getByText('Icon')).toBeInTheDocument()
})

test('NavigationMenuElement renders without error.', () => {
  // Prepare data.
  const navigationElementProperties = {
    path : '/test',
    label: 'TEST',
    icon: <div>Icon</div>,
  }
  let RemixStub = createRemixStub(
    <NavigationMenuElement element={navigationElementProperties} onClick={(): void => {}} />,
  )
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(screen.getByText('TEST', { exact: false })).toBeInTheDocument()
  expect(screen.getByText('Icon')).toBeInTheDocument()
})

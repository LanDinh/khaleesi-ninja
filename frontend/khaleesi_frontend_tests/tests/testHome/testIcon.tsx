import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { MenuIcon, SettingsIcon, HomeIcon } from '../../app/khaleesi/home/icon'


test('Menu Icon gets rendered without errors.', () => {
  // Execute test.
  render(<MenuIcon />)
  // Assert result.
  expect(screen.getByRole('icon')).toBeInTheDocument()
})

test('Setting Icon gets rendered without errors.', () => {
  // Execute test.
  render(<SettingsIcon />)
  // Assert result.
  expect(screen.getByRole('icon')).toBeInTheDocument()
})

test('Home Icon gets rendered without errors.', () => {
  // Execute test.
  render(<HomeIcon />)
  // Assert result.
  expect(screen.getByRole('icon')).toBeInTheDocument()
})

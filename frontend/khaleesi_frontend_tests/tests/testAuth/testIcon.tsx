import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { LoginIcon, LogoutIcon } from '../../app/khaleesi/auth/icon'


test('Login Icon gets rendered without errors.', () => {
  // Execute test.
  render(<LoginIcon />)
  // Assert result.
  expect(screen.getByRole('icon')).toBeInTheDocument()
})

test('Logout Icon gets rendered without errors.', () => {
  // Execute test.
  render(<LogoutIcon />)
  // Assert result.
  expect(screen.getByRole('icon')).toBeInTheDocument()
})

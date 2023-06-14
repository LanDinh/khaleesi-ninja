import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { KitchenIcon, BookIcon } from '../../app/components/icon'


test('Kitchen Icon gets rendered without errors.', () => {
  // Execute test.
  render(<KitchenIcon />)
  // Assert result.
  expect(screen.getByRole('icon')).toBeInTheDocument()
})

test('Book Icon gets rendered without errors.', () => {
  // Execute test.
  render(<BookIcon />)
  // Assert result.
  expect(screen.getByRole('icon')).toBeInTheDocument()
})

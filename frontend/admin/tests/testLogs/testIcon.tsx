import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { LogsIcon, EventsIcon } from '../../app/logs/icon'


test('Logs Icon gets rendered without errors.', () => {
  // Execute test.
  render(<LogsIcon />)
  // Assert result.
  expect(screen.getByRole('icon')).toBeInTheDocument()
})

test('Events Icon gets rendered without errors.', () => {
  // Execute test.
  render(<EventsIcon />)
  // Assert result.
  expect(screen.getByRole('icon')).toBeInTheDocument()
})

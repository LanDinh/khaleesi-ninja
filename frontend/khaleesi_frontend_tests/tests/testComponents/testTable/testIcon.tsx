import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import {
  FirstIcon,
  PreviousIcon,
  NextIcon,
  LastIcon,
} from '../../../app/khaleesi/components/table/icon'


test('First Icon gets rendered without errors.', () => {
  // Execute test.
  render(<FirstIcon />)
  // Assert result.
  expect(screen.getByRole('icon')).toBeInTheDocument()
})

test('Previous Icon gets rendered without errors.', () => {
  // Execute test.
  render(<PreviousIcon />)
  // Assert result.
  expect(screen.getByRole('icon')).toBeInTheDocument()
})

test('Next Icon gets rendered without errors.', () => {
  // Execute test.
  render(<NextIcon />)
  // Assert result.
  expect(screen.getByRole('icon')).toBeInTheDocument()
})

test('Last Icon gets rendered without errors.', () => {
  // Execute test.
  render(<LastIcon />)
  // Assert result.
  expect(screen.getByRole('icon')).toBeInTheDocument()
})

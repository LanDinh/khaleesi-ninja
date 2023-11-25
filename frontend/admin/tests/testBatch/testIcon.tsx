import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { BatchIcon } from '../../app/batch/icon'


test('Batch Icon gets rendered without errors.', () => {
  // Execute test.
  render(<BatchIcon />)
  // Assert result.
  expect(screen.getByRole('icon')).toBeInTheDocument()
})

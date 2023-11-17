import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { Content } from '../../app/khaleesi/home/content'


test('Content gets rendered without errors.', () => {
  // Execute test.
  render(<Content>TEST</Content>)
  // Assert result.
  expect(screen.getByText('TEST')).toBeInTheDocument()
})

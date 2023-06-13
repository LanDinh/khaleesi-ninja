import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { ErrorPage } from '../../app/khaleesi/components/error'
import { createRemixStub } from '../util/remixStub'


afterAll(() => {
  jest.clearAllMocks()
})

test('ErrorPage renders unknown errors.', (): void => {
  // Prepare data.
  let RemixStub = createRemixStub(<ErrorPage />)
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(screen.getByText('Woops!', { exact: false })).toBeInTheDocument()
  expect(screen.getByText('dragon', { exact: false })).toBeInTheDocument()
})
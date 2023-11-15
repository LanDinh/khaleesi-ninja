import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { BreadCrumbs } from '../../app/khaleesi/navigation/breadcrumb'
import { Content } from '../../app/khaleesi/components/content'


jest.mock('../../app/khaleesi/navigation/breadcrumb')


test('Content gets rendered without errors.', () => {
  // Prepare data.
  const mockBreadCrumbs = BreadCrumbs as jest.MockedFunction<typeof BreadCrumbs>
  mockBreadCrumbs.mockImplementation(() => <></>)
  // Execute test.
  render(<Content>TEST</Content>)
  // Assert result.
  expect(mockBreadCrumbs).toHaveBeenCalled()
  expect(screen.getByText('TEST')).toBeInTheDocument()
})

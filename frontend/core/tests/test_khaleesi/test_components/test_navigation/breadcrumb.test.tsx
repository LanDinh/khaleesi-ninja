import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { breadcrumb } from '../../../../app/khaleesi/components/navigation/breadcrumb'
import { createRemixStub } from '../../../util/remixStub'


test('', () => {
  // Prepare data.
  const Icon = <div>TEST</div>
  const match = {
    id: 'test',
    pathname: '',
    params  : {},
    data    : null
  }
  let RemixStub = createRemixStub(breadcrumb({ path: '/some/path', icon: Icon }).breadcrumb(match))
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(screen.getByText('TEST')).toBeInTheDocument()
  expect(screen.getByRole('link')).toHaveAttribute('href', '/some/path')
})

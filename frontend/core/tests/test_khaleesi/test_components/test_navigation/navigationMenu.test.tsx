import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { NavigationMenu } from '../../../../app/khaleesi/components/navigation/navigationMenu'
import { MenuIcon } from '../../../../app/khaleesi/components/icon'
import type { NavigationElement } from '../../../../app/navigationData'
import { createRemixStub } from '../../../util/remixStub'


beforeAll(() => {
  jest.mock('../../../../app/khaleesi/components/icon')
  jest.mock('../../../../app/navigationData', (): NavigationElement[] => (
    [
      {
        path: 'alpha',
        label: 'ALPHA',
        icon: <>a</>,
        children: [ { path: '1', label: 'ONE', icon: <>1</> } ],
      },
      {
        path: 'beta',
        label: 'BETA',
        icon: <>b</>,
        children: [ { path: '2', label: 'TWO', icon: <>2</> } ],
      },
    ]
  ))
})

test('Navigation menu renders without errors.', () => {
  // Prepare data.
  const mockMenuIcon = MenuIcon as jest.MockedFunction<typeof MenuIcon>
  mockMenuIcon.mockImplementation(() => <></>)
  let RemixStub = createRemixStub(<NavigationMenu />, '', '/alpha')
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(mockMenuIcon).toHaveBeenCalled()
  expect(screen.getByText('ALPHA')).toBeInTheDocument()
  expect(screen.getByText('BETA')).toBeInTheDocument()
  expect(screen.getByText('ONE')).toBeInTheDocument()
  expect(screen.getByText('TWO')).toBeInTheDocument()
  expect(screen.getByText('a')).toBeInTheDocument()
  expect(screen.getByText('b')).toBeInTheDocument()
  expect(screen.getByText('1')).toBeInTheDocument()
  expect(screen.getByText('2')).toBeInTheDocument()
  expect(screen.getByText('ALPHA')).toHaveAttribute("open")
  expect(screen.getByText('BETA')).not.toHaveAttribute("open")
})

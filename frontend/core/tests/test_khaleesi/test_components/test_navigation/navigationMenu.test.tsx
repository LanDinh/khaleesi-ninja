import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { NavigationMenu } from '../../../../app/khaleesi/components/navigation/navigationMenu'
import { MenuIcon } from '../../../../app/khaleesi/components/icon'
import type { NavigationElement } from '../../../../app/navigationData'
import { createRemixStub } from '../../../util/remixStub'


jest.mock('../../../../app/khaleesi/components/icon')
jest.mock('../../../../app/navigationData', (): { navigationData: NavigationElement[] } => ({
    navigationData: [
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
    ],
}))

test('Navigation menu renders without errors.', () => {
  // Prepare data.
  const mockMenuIcon = MenuIcon as jest.MockedFunction<typeof MenuIcon>
  mockMenuIcon.mockImplementation(() => <></>)
  let RemixStub = createRemixStub(<NavigationMenu />, '', '/alpha')
  // Execute test.
  render(<RemixStub initialEntries={['/alpha']}/>)
  // Assert result.
  expect(mockMenuIcon).toHaveBeenCalled()
  expect(screen.getByText('ALPHA', { exact: false })).toBeInTheDocument()
  expect(screen.getByText('BETA', { exact: false })).toBeInTheDocument()
  expect(screen.getByText('ONE', { exact: false })).toBeInTheDocument()
  expect(screen.getByText('TWO', { exact: false })).toBeInTheDocument()
  expect(screen.getByText('a ', { exact: false })).toBeInTheDocument()
  expect(screen.getByText('b ', { exact: false })).toBeInTheDocument()
  expect(screen.getByText('1 ', { exact: false })).toBeInTheDocument()
  expect(screen.getByText('2 ', { exact: false })).toBeInTheDocument()
  expect(
    screen.getByText('ALPHA', { exact: false }).parentElement!.parentElement!.parentElement
  ).toHaveAttribute('open')
  expect(
    screen.getByText('BETA', { exact: false }).parentElement!.parentElement!.parentElement
  ).not.toHaveAttribute('open')
})

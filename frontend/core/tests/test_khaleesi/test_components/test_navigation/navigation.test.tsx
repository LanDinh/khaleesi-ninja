import '@testing-library/jest-dom'
import { render } from '@testing-library/react'
import { Navigation } from '../../../../app/khaleesi/components/navigation/navigation'
import { NavigationMenu } from '../../../../app/khaleesi/components/navigation/navigationMenu'
import { SettingsIcon, LoginIcon } from '../../../../app/khaleesi/components/icon'
import { createRemixStub } from '../../../util/remixStub'


jest.mock('../../../../app/khaleesi/components/navigation/navigationMenu')
jest.mock('../../../../app/khaleesi/components/icon')


test('Navigation gets rendered without errors.', () => {
  // Prepare data.
  const mockSettingsIcon = SettingsIcon as jest.MockedFunction<typeof SettingsIcon>
  mockSettingsIcon.mockImplementation(() => <></>)
  const mockLoginIcon = LoginIcon as jest.MockedFunction<typeof LoginIcon>
  mockLoginIcon.mockImplementation(() => <></>)
  const mockNavigationMenu = NavigationMenu as jest.MockedFunction<typeof NavigationMenu>
  mockNavigationMenu.mockImplementation(() => <></>)
  let RemixStub = createRemixStub(<Navigation />)
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(mockSettingsIcon).toHaveBeenCalled()
  expect(mockLoginIcon).toHaveBeenCalled()
  expect(mockNavigationMenu).toHaveBeenCalled()
})

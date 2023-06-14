import '@testing-library/jest-dom'
import { render } from '@testing-library/react'
import { NavigationBar } from '../../../../app/khaleesi/components/navigation/navigationBar'
import { MenuIcon, SettingsIcon, LoginIcon } from '../../../../app/khaleesi/components/icon'
import { createRemixStub } from '../../../util/remixStub'


jest.mock('../../../../app/khaleesi/components/icon')


test('App gets rendered without errors.', () => {
  // Prepare data.
  const mockMenuIcon = MenuIcon as jest.MockedFunction<typeof MenuIcon>
  mockMenuIcon.mockImplementation(() => <></>)
  const mockSettingsIcon = SettingsIcon as jest.MockedFunction<typeof SettingsIcon>
  mockSettingsIcon.mockImplementation(() => <></>)
  const mockLoginIcon = LoginIcon as jest.MockedFunction<typeof LoginIcon>
  mockLoginIcon.mockImplementation(() => <></>)
  let RemixStub = createRemixStub(<NavigationBar />)
  // Execute test.
  render(<RemixStub />)
  // Assert result.
  expect(mockMenuIcon).toHaveBeenCalled()
  expect(mockSettingsIcon).toHaveBeenCalled()
  expect(mockLoginIcon).toHaveBeenCalled()
})

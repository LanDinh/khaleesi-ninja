import { useMatches } from '@remix-run/react'
import { LoginIcon, SettingsIcon } from '../icon'
import { NavigationMenu } from './navigationMenu'


export function Navigation(): JSX.Element {
  const matches = useMatches()

  return <nav id="khaleesi-navigation" className="khaleesi-bar">
    <NavigationMenu />
    <div id="khaleesi-navigation-breadcrumbs" className="khaleesi-navigation-icon">
      {
        matches
          .filter((match) => match.handle && match.handle.breadcrumb)
          .map((match) => match.handle!.breadcrumb(match))
      }
    </div>
    <div id="khaleesi-navigation-common" className="khaleesi-navigation-icon">
      <SettingsIcon />
      <LoginIcon />
    </div>
  </nav>
}
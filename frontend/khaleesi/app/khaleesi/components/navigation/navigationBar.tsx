import { useMatches } from '@remix-run/react'
import { MenuIcon, LoginIcon, SettingsIcon } from '../icon'


export function NavigationBar(): JSX.Element {
  const matches = useMatches()

  return <nav id="khaleesi-navigation" className="khaleesi-bar">
    <MenuIcon id="khaleesi-navigation-menu" />
    <div id="khaleesi-navigation-breadcrumbs">
      {
        matches
          .filter((match) => match.handle && match.handle.breadcrumb)
          .map((match) => match.handle!.breadcrumb(match))
      }
    </div>
    <div id="khaleesi-navigation-common">
      <SettingsIcon />
      <LoginIcon />
    </div>
  </nav>
}
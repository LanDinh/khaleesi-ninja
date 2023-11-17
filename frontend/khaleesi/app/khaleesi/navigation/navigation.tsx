import { useState, useEffect } from 'react'
import { useMatches } from '@remix-run/react'
import { navigationData } from '../../navigationData'
import { topNavigationData, bottomNavigationData } from './commonNavigationData'
import { MenuIcon } from '../home/icon'
import type { RouteMatch } from './breadcrumb'
import type { NavigationElementProperties } from './navigationElement'
import { NavigationMenuElement } from './navigationElement'

function NavigationMenuElementWithChildren({
  element,
  matches,
  closeMenu,
}: {
  element: NavigationElementProperties,
  matches: RouteMatch[],
  closeMenu: () => void,
}): JSX.Element {
  if (!element.children) {
    return <NavigationMenuElement element={element} onClick={closeMenu} />
  }
  const isOnPath = matches.map((match) => match.pathname).includes(element.path)
  return <details open={isOnPath} >
    <summary> <NavigationMenuElement element={element} onClick={closeMenu} /></summary>
    <div className="khaleesi-navigation-item-child">
      {element.children.map((child) => (
        <NavigationMenuElementWithChildren
          element={child}
          matches={matches}
          closeMenu={closeMenu}
          key={element.path}
        />
      ))}
    </div>
  </details>
}


export function Navigation(): JSX.Element {
  const matches: RouteMatch[] = useMatches() as RouteMatch[]
  const [ open , setOpen ] = useState(false)
  const closeMenu = (): void => setOpen(!open)

  useEffect(() => {
    document.getElementById('khaleesi-navigation')!.toggleAttribute('open')
  }, [ open ])

  return <details id="khaleesi-navigation">
    <div id="khaleesi-navigation-background" onClick={closeMenu}/>
    <summary id="khaleesi-navigation-button" className="khaleesi-navigation-icon">
      <MenuIcon />
    </summary>
    <nav id="khaleesi-navigation-list">
      {topNavigationData.map((element) => (
        <NavigationMenuElementWithChildren
          element={element}
          matches={matches}
          closeMenu={closeMenu}
          key={element.path}
        />
      ))}
      {navigationData.map((element) => (
        <NavigationMenuElementWithChildren
          element={element}
          matches={matches}
          closeMenu={closeMenu}
          key={element.path}
        />
      ))}
      {bottomNavigationData.map((element) => (
        <NavigationMenuElementWithChildren
          element={element}
          matches={matches}
          closeMenu={closeMenu}
          key={element.path}
        />
      ))}
    </nav>
  </details>
}

import { useState, useEffect } from 'react'
import { useMatches } from '@remix-run/react'
import { MenuIcon } from '../home/icon'
import type { RouteMatch } from './breadcrumb'
import type { NavigationElementProperties } from './navigationElement'
import { NavigationMenuElement } from './navigationElement'


function NavigationMenuGroup({ navigationData, matches, closeMenu }: {
    navigationData: NavigationElementProperties[],
    matches       : RouteMatch[],
    closeMenu     : () => void,
  }
): JSX.Element {
  return <>
    {navigationData.map((element) => (
      <NavigationMenuElementWithChildren
        element={element}
        matches={matches}
        closeMenu={closeMenu}
        key={element.path}
      />
    ))}
  </>
}


function NavigationMenuElementWithChildren({
  element,
  matches,
  closeMenu,
}: {
  element  : NavigationElementProperties,
  matches  : RouteMatch[],
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


export function Navigation(
  { top, middle, bottom }: {
    top   : NavigationElementProperties[],
    middle: NavigationElementProperties[],
    bottom: NavigationElementProperties[],
  }): JSX.Element {
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
      <NavigationMenuGroup navigationData={top} matches={matches} closeMenu={closeMenu} />
      <NavigationMenuGroup navigationData={middle} matches={matches} closeMenu={closeMenu} />
      <NavigationMenuGroup navigationData={bottom} matches={matches} closeMenu={closeMenu} />
    </nav>
  </details>
}

import { useState, useEffect } from 'react'
import { NavLink, useMatches } from '@remix-run/react'
import type { NavigationElement } from '../../../navigationData'
import { navigationData } from '../../../navigationData'
import { MenuIcon } from '../icon'
import type { RouteMatch } from './breadcrumb'



function getNavigationElement(
  element   : NavigationElement,
  elementPath: string,
  closeMenu : () => void,
  key      : string = '',
): JSX.Element {
  return <div className="khaleesi-navigation-menu-item" key={key}>
    <NavLink to={elementPath} onClick={closeMenu}>{element.icon} {element.label}</NavLink>
  </div>
}

function getNavigationElementWithChildren(
  element   : NavigationElement,
  parentPath: string,
  matches   : RouteMatch[],
  closeMenu : () => void,
): JSX.Element {
  const elementPath = `${parentPath}/${element.path}`
  if (!element.children) {
    return getNavigationElement(element, elementPath, closeMenu, element.path)
  }
  const isOnPath = matches.map((match) => match.pathname).includes(elementPath)
  return <details key={element.path} open={isOnPath} >
    <summary> {getNavigationElement(element, elementPath, closeMenu)}</summary>
    <div className="khaleesi-navigation-menu-item-child">
      {element.children.map((child) => (
        getNavigationElementWithChildren(child, elementPath, matches, closeMenu))
      )}
    </div>
  </details>
}


export function NavigationMenu(): JSX.Element {
  const matches = useMatches()
  const [ open , setOpen ] = useState(false)
  const closeMenu = (): void => setOpen(!open)

  useEffect(() => {
    document.getElementById('khaleesi-navigation-menu')!.toggleAttribute('open')
  }, [ open ])

  return <details id="khaleesi-navigation-menu">
    <summary id="khaleesi-navigation-menu-button" className="khaleesi-navigation-icon">
      <MenuIcon />
    </summary>
    <nav id="khaleesi-navigation-menu-list">
      {navigationData.map((element) => (
        getNavigationElementWithChildren(element, '', matches, closeMenu))
      )}
    </nav>
  </details>
}
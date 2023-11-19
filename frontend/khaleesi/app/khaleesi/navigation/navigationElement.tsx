import { Link, NavLink } from '@remix-run/react'
import { iconLookup as commonIconLookup } from './commonNavigationData'
import { iconLookup } from '../../navigationData'


export type NavigationElementProperties = {
  path       : string,
  label      : string,
  icon       : JSX.Element,
  children?  : NavigationElementProperties[]
}


export function NavigationElement(
  { element }: {element: NavigationElementProperties},
): JSX.Element {
  return <Link to={element.path} key={element.path}>{element.icon} {element.label}</Link>
}


export function NavigationMenuElement({
  element,
  onClick,
}: {
  element: NavigationElementProperties,
  onClick: () => void,
}): JSX.Element {
  let icon = <div>Icon missing!</div>
  if (commonIconLookup.hasOwnProperty(element.label)) {
    icon = commonIconLookup[element.label]
  } else if (iconLookup.hasOwnProperty(element.label)) {
    icon = iconLookup[element.label]
  }
  return <div className="khaleesi-navigation-item">
    <NavLink to={element.path} onClick={onClick}>{icon} {element.label}</NavLink>
  </div>
}

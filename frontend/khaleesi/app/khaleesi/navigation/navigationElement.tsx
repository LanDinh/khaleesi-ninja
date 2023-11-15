import { Link, NavLink } from '@remix-run/react'


export type NavigationElementProperties = {
  path     : string,
  label    : string,
  icon     : JSX.Element,
  children?: NavigationElementProperties[]
}

type NavigationMenuElementProperties = {
  element: NavigationElementProperties
  onClick: () => void
}


export function NavigationElement(
  { element }: {element: NavigationElementProperties},
  ): JSX.Element {
  return <Link to={element.path} key={element.path}>{element.icon} {element.label}</Link>
}


export function NavigationMenuElement({
  element,
  onClick,
}: NavigationMenuElementProperties): JSX.Element {
  return <div className="khaleesi-navigation-item">
    <NavLink to={element.path} onClick={onClick}>{element.icon} {element.label}</NavLink>
  </div>
}

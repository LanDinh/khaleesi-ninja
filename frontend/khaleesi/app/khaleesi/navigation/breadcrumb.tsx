import { useMatches } from '@remix-run/react'
import type { UIMatch } from '@remix-run/react'
import type { NavigationElementProperties } from './navigationElement'
import { NavigationElement } from './navigationElement'


export function breadcrumb(
  element: NavigationElementProperties,
): { breadcrumb: () => JSX.Element } {
  return {
    breadcrumb: (): JSX.Element => <NavigationElement element={element} />,
  }
}
export type RouteMatch = UIMatch<any, { breadcrumb?: (match?: RouteMatch) => JSX.Element }>

export function BreadCrumbs(): JSX.Element {
  const rawMatches: RouteMatch[] = useMatches() as RouteMatch[]
  const matches = rawMatches.filter((match) => match.handle && match.handle.breadcrumb)

  return <div id="khaleesi-navigation-breadcrumbs">
    {
      matches.map((match, index) => <span key={match.id}>
        {match.handle.breadcrumb!(match)}{index < matches.length - 1 && '>'}
      </span>)
    }
  </div>
}

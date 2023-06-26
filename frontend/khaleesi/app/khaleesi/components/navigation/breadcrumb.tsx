import type { Params } from '@remix-run/react'
import { useMatches } from '@remix-run/react'
import type { NavigationElementProperties } from './navigationElement'
import { NavigationElement } from './navigationElement'


export type RouteMatch = {
  id      : string
  pathname: string
  params  : Params<string>
  data    : any
  handle? : { breadcrumb?: () => JSX.Element }
}
export function breadcrumb(
  element: NavigationElementProperties,
): { breadcrumb: () => JSX.Element } {
  return {
    breadcrumb: (): JSX.Element => <NavigationElement element={element} />,
  }
}

export function BreadCrumbs(): JSX.Element {
  const matches = useMatches().filter((match) => match.handle && match.handle.breadcrumb)

  return <div id="khaleesi-navigation-breadcrumbs">
    {
      matches.map((match, index) => <span key={match.id}>
        {match.handle!.breadcrumb(match)}{index < matches.length - 1 && '>'}
      </span>)
    }
  </div>
}

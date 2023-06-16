import type { Params } from '@remix-run/react'
import { Link } from '@remix-run/react'


type BreadcrumbProperties = {
  path: string
  icon: JSX.Element
}

export type RouteMatch = {
  id      : string
  pathname: string
  params  : Params<string>
  data    : any
  handle? : { breadcrumb?: (props: BreadcrumbProperties) => JSX.Element }
}
export function breadcrumb(
  { path, icon }: BreadcrumbProperties,
): { breadcrumb: (match: RouteMatch) => JSX.Element } {
  return {
    breadcrumb: (match): JSX.Element => <Link to={path} key={match.id}>{icon}</Link>,
  }
}

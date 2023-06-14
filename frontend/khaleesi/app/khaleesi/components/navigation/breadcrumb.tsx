import { Link } from '@remix-run/react'


type BreadcrumbProperties = {
  path: string
  icon: JSX.Element
}
export function breadcrumb(
  { path, icon }: BreadcrumbProperties,
): { breadcrumb: () => JSX.Element } {
  return {
    breadcrumb: (): JSX.Element => <Link to={path}>{icon}</Link>,
  }
}

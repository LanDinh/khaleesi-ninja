import { Outlet } from '@remix-run/react'
import type {
  NavigationElementProperties,
} from '../khaleesi/navigation/navigationElement'
import { breadcrumb } from '../khaleesi/navigation/breadcrumb'
import { BookIcon } from '../components/icon'


export const navigationProperties: NavigationElementProperties = {
  path : '/kitchen/cookbook',
  label: 'Cookbook',
  icon : <BookIcon />,
}


export const handle = {
  ...breadcrumb(navigationProperties),
}

export default function RecipeRoute(): JSX.Element {
  return (
    <div>
      <h1>Cookbook</h1>
      <main>
        <Outlet />
      </main>
    </div>
  )
}
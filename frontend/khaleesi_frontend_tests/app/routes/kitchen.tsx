import { Outlet } from '@remix-run/react'
import type {
  NavigationElementProperties,
} from '../khaleesi/components/navigation/navigationElement'
import { breadcrumb } from '../khaleesi/components/navigation/breadcrumb'
import { KitchenIcon } from '../components/icon'


export const navigationProperties: NavigationElementProperties = {
  path : '/kitchen',
  label: 'Kitchen',
  icon : <KitchenIcon />,
}


export const handle = {
  ...breadcrumb(navigationProperties),
}


export default function KitchenRoute(): JSX.Element {
  return (
    <div>
      <h1>Kitchen</h1>
      <main>
        <Outlet />
      </main>
    </div>
  )
}
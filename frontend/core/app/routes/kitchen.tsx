import { Outlet } from '@remix-run/react'
import { breadcrumb } from '../khaleesi/components/navigation/breadcrumb'
import { KitchenIcon } from '../components/icon'


export const handle = {
  ...breadcrumb({ path: '/kitchen', icon: <KitchenIcon /> }),
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
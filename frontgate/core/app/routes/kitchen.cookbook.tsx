import { Outlet } from '@remix-run/react'
import { breadcrumb } from '../khaleesi/components/navigation/breadcrumb'
import { BookIcon } from '../components/icon'


export const handle = {
  ...breadcrumb({ path: '/kitchen/cookbook', icon: <BookIcon /> }),
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
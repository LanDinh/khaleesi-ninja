import { Outlet } from '@remix-run/react'


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
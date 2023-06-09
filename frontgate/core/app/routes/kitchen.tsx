import { Outlet } from '@remix-run/react'


export default function KitchenRoute() {
  return (
    <div>
      <h1>Kitchen</h1>
      <main>
        <Outlet />
      </main>
    </div>
  )
}
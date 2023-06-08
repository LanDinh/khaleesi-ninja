import { Outlet } from '@remix-run/react'

export default function RecipeRoute() {
  return (
    <div>
      <h1>Cookbook</h1>
      <main>
        <Outlet />
      </main>
    </div>
  )
}
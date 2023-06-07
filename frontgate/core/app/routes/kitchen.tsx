import { Outlet } from '@remix-run/react'
import type { LinksFunction } from '@remix-run/node'
import styles from '../khaleesi/core/styles/index.css'

export const links: LinksFunction = () => [
  // Font.
  { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Roboto&display=swap' },
  // Style.
  { rel: 'stylesheet', href: styles },
]

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
import { Outlet, LinksFunction } from "@remix-run/react"
import styles from "../khaleesi/core/styles/index.css"

export const links: LinksFunction = () => [
  { rel: "stylesheet", href: styles },
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
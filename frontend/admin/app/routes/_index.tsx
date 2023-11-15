import type { MetaFunction, LinksFunction } from "@remix-run/node"
import styles from '../khaleesi/styles/index.css'

export const meta: MetaFunction = () => {
  return [
    { title: "khaleesi.ninja | New Frontend" },
    { name: "description", content: "Khaleesi's New Frontend." },
  ]
}

export const links: LinksFunction = () => [
  { rel: "stylesheet", href: styles },
]


export default function Index() {
  return (
    <div>New Frontend</div>
  )
}

import type { V2_MetaFunction, LinksFunction } from "@remix-run/node"
import styles from "../khaleesi/core/styles/index.css"

export const meta: V2_MetaFunction = () => {
  return [
    { title: "khaleesi.ninja" },
    { name: "description", content: "Khaleesi's Dragonpit." },
  ]
}

export const links: LinksFunction = () => [
  { rel: "stylesheet", href: styles },
]


export default function Index() {
  return (
    <div><ul>
      <li><a href="/kitchen">Kitchen</a></li>
    </ul></div>
  )
}

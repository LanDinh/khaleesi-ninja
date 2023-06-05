import type { V2_MetaFunction } from "@remix-run/node"

export const meta: V2_MetaFunction = () => {
  return [
    { title: "khaleesi.ninja" },
    { name: "description", content: "Khaleesi's Dragonpit." },
  ]
}

export default function Index() {
  return (
    <div>Dragonpit</div>
  )
}

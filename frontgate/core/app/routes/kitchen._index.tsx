import type { V2_MetaFunction } from '@remix-run/node'

export const meta: V2_MetaFunction = () => {
  return [
    { title: 'khaleesi.ninja | Kitchen' },
    { name: 'description', content: 'Khaleesi\'s Dragonpit: the kitchen for hungry dragons.' },
  ]
}

export default function KitchenIndex() {
  return (
    <div><ul>
      <li><a href="/kitchen/recipe">Recipes</a></li>
    </ul></div>
  )
}

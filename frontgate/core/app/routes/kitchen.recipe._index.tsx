import type { V2_MetaFunction } from '@remix-run/node'

export const meta: V2_MetaFunction = () => {
  return [
    { title: 'khaleesi.ninja | Recipes' },
    { name: 'description', content: 'Khaleesi\'s Dragonpit: recipes for hungry dragons.' },
  ]
}

export default function RecipeIndex() {
  return (
    <div><ul>
      <li>Example</li>
    </ul></div>
  )
}

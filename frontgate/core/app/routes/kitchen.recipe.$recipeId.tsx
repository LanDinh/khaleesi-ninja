import type { V2_MetaFunction } from '@remix-run/node'
import { useLoaderData } from '@remix-run/react'
import { Recipe } from '../khaleesi/proto/core_kitchen_pb'
import { RECIPE_CLIENT_MOCK } from '../khaleesi/core/mock/proto'


export const meta: V2_MetaFunction = () => {
  return [
    { title: 'khaleesi.ninja | Recipe' },
    { name: 'description', content: 'Khaleesi\'s Dragonpit: a recipe for hungry dragons.' },
  ]
}

export async function loader(): Promise<Recipe.AsObject[]> {
  return RECIPE_CLIENT_MOCK.get_recipes()
}

export default function RecipeInstanceRoute() {
  const recipes = useLoaderData<typeof loader>();
  return (
    <ul>
      { recipes.map((recipe) => <li>{recipe.name}</li>) }
    </ul>
  )
}
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

export async function loader(): Promise<Recipe.AsObject> {
  return RECIPE_CLIENT_MOCK.get_recipe()
}

export default function RecipeInstanceRoute() {
  const recipe = useLoaderData<typeof loader>();
  return (
    <div>
      { recipe.name }
    </div>
  )
}
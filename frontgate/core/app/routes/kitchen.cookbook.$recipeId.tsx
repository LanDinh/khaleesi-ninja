import type { V2_MetaFunction, LoaderArgs } from '@remix-run/node'
import { useLoaderData, useParams } from '@remix-run/react'
import type { Recipe } from '../khaleesi/proto/core_kitchen_pb'
import { RECIPE_CLIENT_MOCK } from '../khaleesi/temp/proto'


export const meta: V2_MetaFunction = () => {
  return [
    { title: 'khaleesi.ninja | Recipe' },
    { name: 'description', content: 'Khaleesi\'s Dragonpit: a recipe for hungry dragons.' },
  ]
}

export function ErrorBoundary() {
  const { recipeId } = useParams()
  return <div>
    There was an error loading the recipe with the ID { recipeId }.
  </div>
}

export async function loader({ params }: LoaderArgs): Promise<Recipe.AsObject> {
  return RECIPE_CLIENT_MOCK.getRecipe(params.recipeId)
}

export default function RecipeInstanceRoute() {
  const recipe = useLoaderData<typeof loader>()
  return (
    <div>
      <h2>{ recipe.name }</h2>
      <p>{ recipe.description }</p>
    </div>
  )
}
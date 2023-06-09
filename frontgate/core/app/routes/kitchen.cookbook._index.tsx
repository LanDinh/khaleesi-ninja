import type { V2_MetaFunction } from '@remix-run/node'
import { useLoaderData } from '@remix-run/react'
import { RECIPE_CLIENT_MOCK } from '../khaleesi/core/mock/proto'
import type { Recipe } from '../khaleesi/proto/core_kitchen_pb'

export const meta: V2_MetaFunction = () => {
  return [
    { title: 'khaleesi.ninja | Cookbook' },
    { name: 'description', content: 'Khaleesi\'s Dragonpit: a cookbook for hungry dragons.' },
  ]
}

export async function loader(): Promise<Recipe.AsObject[]> {
  return RECIPE_CLIENT_MOCK.getRecipes()
}

export default function RecipeIndex() {
  const recipes = useLoaderData<typeof loader>()

  return (
    <ul>
      { recipes.map((recipe) => <li key={recipe.recipeId}>
        <a href={'/kitchen/cookbook/' + recipe.recipeId}>{recipe.name}</a>
      </li>)}
    </ul>
  )
}

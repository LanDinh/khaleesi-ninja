// Fake gRPC clients until the interfaces are implemented.

import { Recipe } from '../../proto/core_kitchen_pb'


class RecipeClientMock {
  async get_recipe(): Promise<Recipe.AsObject> {
    const recipe_a: Recipe = new Recipe()
    recipe_a.setName('Recipe A')
    recipe_a.setDescription('Cooking something delicious')

    return new Promise((resolve, reject) => {
      setTimeout(() => {
        resolve(recipe_a.toObject())
      }, 1000) // 1s.
    })
  }
}

export const RECIPE_CLIENT_MOCK = new RecipeClientMock()

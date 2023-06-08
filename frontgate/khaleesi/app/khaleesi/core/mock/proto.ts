// Fake gRPC clients until the interfaces are implemented.

import { Recipe } from '../../proto/core_kitchen_pb'


class RecipeClientMock {

  recipes: Recipe.AsObject[]

  constructor() {
    const recipe_a: Recipe = new Recipe()
    recipe_a.setRecipeId('0');
    recipe_a.setName('Recipe A')
    recipe_a.setDescription('Cooking something delicious')
    this.recipes = [ recipe_a.toObject() ]
  }
  async get_recipes(): Promise<Recipe.AsObject[]> {

    return new Promise((resolve, reject) => {
      setTimeout(() => {
        resolve(this.recipes)
      }, 1000) // 1s.
    })
  }
}

export const RECIPE_CLIENT_MOCK = new RecipeClientMock()

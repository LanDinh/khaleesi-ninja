// Fake gRPC clients until the interfaces are implemented.

import { Recipe } from '../../proto/core_kitchen_pb'


class RecipeClientMock {

  recipes: Recipe.AsObject[]

  constructor() {
    const recipeA: Recipe = new Recipe()
    recipeA.setRecipeId('0')
    recipeA.setName('Recipe A')
    recipeA.setDescription('Cooking something delicious')

    const recipeB: Recipe = new Recipe()
    recipeB.setRecipeId('1')
    recipeB.setName('Recipe B')
    recipeB.setDescription('Cooking something awful')

    this.recipes = [ recipeA.toObject(), recipeB.toObject() ]
  }
  async getRecipes(): Promise<Recipe.AsObject[]> {

    return new Promise((resolve, reject) => {
      setTimeout(() => {
        resolve(this.recipes)
      }, 1000) // 1s.
    })
  }

  async getRecipe(id: string | undefined): Promise<Recipe.AsObject> {
    if (!id) {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          reject()
        }, 1000) // 1s.
      })
    }

    for (let recipe of this.recipes) {
      if (recipe.recipeId === id) {
        return new Promise((resolve, reject) => {
          setTimeout(() => {
            resolve(recipe)
          }, 1000) // 1s.
        })
      }
    }

    return new Promise((resolve, reject) => {
      setTimeout(() => {
        reject()
      }, 1000) // 1s.
    })
  }

  async createRecipe(name: string, description: string): Promise<Recipe.AsObject> {
    const newRecipe = new Recipe()
    newRecipe.setRecipeId('2')
    newRecipe.setName(name)
    newRecipe.setDescription(description)
    this.recipes.push(newRecipe.toObject())

    return new Promise((resolve, reject) => {
      setTimeout(() => {
        resolve(newRecipe.toObject())
      }, 1000) // 1s.
    })
  }
}

export const RECIPE_CLIENT_MOCK = new RecipeClientMock()

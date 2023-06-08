// Fake gRPC clients until the interfaces are implemented.

import { Recipe } from '../../proto/core_kitchen_pb'


class RecipeClientMock {

  recipes: Recipe.AsObject[]

  constructor() {
    const recipe_a: Recipe = new Recipe()
    recipe_a.setRecipeId('0')
    recipe_a.setName('Recipe A')
    recipe_a.setDescription('Cooking something delicious')

    const recipe_b: Recipe = new Recipe()
    recipe_b.setRecipeId('1')
    recipe_b.setName('Recipe B')
    recipe_b.setDescription('Cooking something awful')

    this.recipes = [ recipe_a.toObject(), recipe_b.toObject() ]
  }
  async get_recipes(): Promise<Recipe.AsObject[]> {

    return new Promise((resolve, reject) => {
      setTimeout(() => {
        resolve(this.recipes)
      }, 1000) // 1s.
    })
  }

  async get_recipe(id: string | undefined): Promise<Recipe.AsObject> {
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

  async create_recipe(name: string, description: string): Promise<Recipe.AsObject> {
    const new_recipe = new Recipe()
    new_recipe.setRecipeId('2')
    new_recipe.setName(name)
    new_recipe.setDescription(description)
    this.recipes.push(new_recipe.toObject())

    return new Promise((resolve, reject) => {
      setTimeout(() => {
        resolve(new_recipe.toObject())
      }, 1000) // 1s.
    })
  }
}

export const RECIPE_CLIENT_MOCK = new RecipeClientMock()

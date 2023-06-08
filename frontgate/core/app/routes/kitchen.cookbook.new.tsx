import type { ActionArgs } from '@remix-run/node'
import { redirect, json } from '@remix-run/node'
import { useActionData } from '@remix-run/react'
import { RECIPE_CLIENT_MOCK } from '../khaleesi/core/mock/proto'


function validate(data: any): string | void {
  if (!data) {
    return 'Required'
  }
  if (3 > data.length) {
    return 'Too short'
  }
}

export const action = async ({ request }: ActionArgs) => {
  const form = await request.formData()
  const description = form.get('description')
  const name = form.get('name')

  if ('string' !== typeof description || 'string' !== typeof name) {
    return json({ field_errors: null, fields: null, formError: 'wrong type' }, { status: 400 })
  }

  const field_errors = {
    description: validate(description),
    name       : validate(name),
  }

  const fields = {
    description: description,
    name       : name,
  }

  if (Object.values(field_errors).some(Boolean)) {
    return json({ field_errors, fields, formError: null }, { status: 400 })
  }

  const recipe = await RECIPE_CLIENT_MOCK.create_recipe(name, description)
  return redirect(`/kitchen/cookbook/${recipe.recipeId}`)
}

export default function NewRecipeRoute() {
  const action_data = useActionData<typeof action>()
  return (
    <div>
      <form method="post">
        <div>
          <label>
            Name: <input type="text" name="name" defaultValue={action_data?.fields?.name}/>
          </label>
          {action_data?.field_errors?.name ? <p>{action_data.field_errors.name}</p> : null}
        </div>
        <div>
          <label>
            Description: <textarea name="description" defaultValue={action_data?.fields?.description}/>
          </label>
          {action_data?.field_errors?.description ? <p>{action_data.field_errors.description}</p> : null}
        </div>
        <div>
          <button type="submit" className="button">
            Add
          </button>
        </div>
      </form>
    </div>
  )
}
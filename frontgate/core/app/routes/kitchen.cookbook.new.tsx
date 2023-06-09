import type { ActionArgs } from '@remix-run/node'
import { redirect, json } from '@remix-run/node'
import { useActionData, Form } from '@remix-run/react'
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
    return json({ fieldErrors: null, fields: null, formError: 'wrong type' }, { status: 400 })
  }

  const fieldErrors = {
    description: validate(description),
    name       : validate(name),
  }

  const fields = {
    description: description,
    name       : name,
  }

  if (Object.values(fieldErrors).some(Boolean)) {
    return json({ fieldErrors: fieldErrors, fields, formError: null }, { status: 400 })
  }

  const recipe = await RECIPE_CLIENT_MOCK.createRecipe(name, description)
  return redirect(`/kitchen/cookbook/${recipe.recipeId}`)
}

export default function NewRecipeRoute() {
  const actionData = useActionData<typeof action>()
  return (
    <div>
      <Form method="post">
        <div>
          <label>
            Name: <input type="text" name="name" defaultValue={actionData?.fields?.name}/>
          </label>
          {actionData?.fieldErrors?.name ? <p>{actionData.fieldErrors.name}</p> : null}
        </div>
        <div>
          <label>
            Description: <textarea name="description" defaultValue={actionData?.fields?.description}/>
          </label>
          {actionData?.fieldErrors?.description ? <p>{actionData.fieldErrors.description}</p> : null}
        </div>
        <div>
          <button type="submit" className="button">
            Add
          </button>
        </div>
      </Form>
    </div>
  )
}
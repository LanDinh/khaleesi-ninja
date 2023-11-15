import type { MetaFunction, ActionFunctionArgs, TypedResponse } from '@remix-run/node'
import { json } from '@remix-run/node'
import { Form } from '@remix-run/react'
import { createUserSession } from '../khaleesi/auth'


export const meta: MetaFunction = () => {
  return [
    { title: 'khaleesi.ninja | Login' },
    { name: 'description', content: 'Khaleesi\'s Dragonpit: Identify yourself!' },
  ]
}

export const action = async ({ request }: ActionFunctionArgs): Promise<TypedResponse<any>> => {
  const form = await request.formData()
  const user = form.get('user')

  if ('string' !== typeof user) {
    return json({ fieldErrors: null, fields: null, formError: 'wrong type' }, { status: 400 })
  }

  return createUserSession(user, '/')
}


export default function LoginRoute(): JSX.Element {
  return (
    <div>
      <h1>Login</h1>
      <section><Form method="post">
        <label>
          <input type="radio" name="user" value="user" defaultChecked />
          user
        </label>
        <label>
          <input type="radio" name="user" value="admin" />
          admin
        </label>
        <button type="submit" className="button">Login</button>
      </Form></section>
    </div>
  )
}

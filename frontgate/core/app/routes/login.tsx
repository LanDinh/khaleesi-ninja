import type { V2_MetaFunction } from '@remix-run/node'
import type { ActionArgs } from '@remix-run/node'
import { json } from '@remix-run/node'
import { Form } from '@remix-run/react'
import { createUserSession } from '../khaleesi/auth'


export const meta: V2_MetaFunction = () => {
  return [
    { title: 'khaleesi.ninja | Login' },
    { name: 'description', content: 'Khaleesi\'s Dragonpit: Identify yourself!' },
  ]
}

export const action = async ({ request }: ActionArgs) => {
  const form = await request.formData()
  const user = form.get('user')

  console.log('before validation')

  if ('string' !== typeof user) {
    return json({ fieldErrors: null, fields: null, formError: 'wrong type' }, { status: 400 })
  }

  console.log('validation passed')
  return createUserSession(user, '/')
}


export default function LoginRoute() {
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
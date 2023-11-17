import type { MetaFunction, ActionFunctionArgs, TypedResponse } from '@remix-run/node'
import { json, redirect } from '@remix-run/node'
import { Form } from '@remix-run/react'
import { useContext } from 'react'
import { AppContext } from '../components/document'
import { createUserSession, destroySession, getSessionData } from './session'


export const meta: MetaFunction = () => {
  const appContext = useContext(AppContext)  // eslint-disable-line react-hooks/rules-of-hooks

  return [
    { title: `Login | ${appContext.title}` },
    { name: 'description', content: 'Identify yourself!' },
  ]
}

export const action = async ({ request }: ActionFunctionArgs): Promise<TypedResponse<any>> => {
  const { session } = await getSessionData(request).then(value => value.json())
  const form = await request.formData()
  const action = form.get('action')
  const user = form.get('user')

  switch(action) {
    case 'login':
      break
    case 'logout':
      destroySession(session)
      return redirect('/')
    default:
      return json({ fieldErrors: null, fields: null, formError: 'unknown action' }, { status: 400 })
  }

  if ('string' !== typeof user) {
    return json({ fieldErrors: { user: 'wrong type' }, formError: null }, { status: 400 })
  }

  return createUserSession(user, '/')
}


export function LoginRoute(): JSX.Element {
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
        <button type="submit" className="button" name="action" value="login">Login</button>
        <button type="submit" className="button" name="action" value="logout">Logout</button>
      </Form></section>
    </div>
  )
}

import type { MetaFunction, ActionFunctionArgs, TypedResponse } from '@remix-run/node'
import { json } from '@remix-run/node'
import { Form } from '@remix-run/react'
import { useContext } from 'react'
import { AppContext } from '../home/document'
import { breadcrumb } from '../navigation/breadcrumb'
import { loginNavigationData } from '../navigation/commonNavigationData'
import { Session } from './session.server'


export const handle = {
  ...breadcrumb(loginNavigationData),
}


export const meta: MetaFunction = () => {
  const appContext = useContext(AppContext)  // eslint-disable-line react-hooks/rules-of-hooks

  return [
    { title: `Login | ${appContext.title}` },
    { name: 'description', content: 'Identify yourself!' },
  ]
}

export const action = async ({ request }: ActionFunctionArgs): Promise<TypedResponse<any>> => {
  const session = new Session()
  await session.init(request)
  const form = await request.formData()
  const user = form.get('user')

  if ('string' !== typeof user) {
    return json({ fieldErrors: { user: 'wrong type' }, formError: null }, { status: 400 })
  }

  return session.create(user, '/')
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
        <button type="submit" className="button" name="action">Login</button>
      </Form></section>
    </div>
  )
}

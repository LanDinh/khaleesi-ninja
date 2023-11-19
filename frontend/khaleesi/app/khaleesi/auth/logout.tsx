import type { MetaFunction, TypedResponse, ActionFunctionArgs } from '@remix-run/node'
import { Form } from '@remix-run/react'
import { useContext } from 'react'
import { AppContext } from '../home/document'
import { breadcrumb } from '../navigation/breadcrumb'
import { logoutNavigationData } from '../navigation/commonNavigationData'
import { Session } from './session.server'


export const handle = {
  ...breadcrumb(logoutNavigationData),
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
  return session.destroy('/')
}


export function LogoutRoute(): JSX.Element {
  return (
    <div>
      <h1>Logout</h1>
      <section><Form method="post">
        <button type="submit" className="button" name="action">Logout</button>
      </Form></section>
    </div>
  )
}

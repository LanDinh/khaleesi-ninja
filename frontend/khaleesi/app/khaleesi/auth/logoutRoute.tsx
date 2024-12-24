import { Form } from '@remix-run/react'
import type { MetaFunction, ActionFunctionArgs, TypedResponse } from '@remix-run/node'
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
    { title: `Logout | ${appContext.title}` },
    { name: 'description', content: 'Logout.' },
  ]
}

export async function action({ request }: ActionFunctionArgs): Promise<TypedResponse<never>> {
  const session = new Session()
  await session.init(request)
  return session.destroy('/')
}


export default function LogoutRoute(): JSX.Element {
  return (
    <div>
      <h1>Logout</h1>
      <section><Form method="post">
        <button type="submit" className="button" name="action">Logout</button>
      </Form></section>
    </div>
  )
}

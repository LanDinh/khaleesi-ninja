import type { MetaFunction, TypedResponse, ActionFunctionArgs } from '@remix-run/node'
import { Form } from '@remix-run/react'
import { useContext } from 'react'
import { AppContext } from '../home/document'
import { breadcrumb } from '../navigation/breadcrumb'
import { logoutNavigationData } from '../navigation/commonNavigationData'


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

export const action = async ({ request }: ActionFunctionArgs): Promise<TypedResponse<any>> => {  // eslint-disable-line @typescript-eslint/no-explicit-any, max-len
  const { Session } = await import('./session.server')
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

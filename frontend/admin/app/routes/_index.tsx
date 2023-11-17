import type { MetaFunction } from '@remix-run/node'
import { useContext } from 'react'
import { AppContext } from '../khaleesi/home/document'


export const meta: MetaFunction = () => {
  // eslint-disable-next-line react-hooks/rules-of-hooks
  const appContext = useContext(AppContext)

  return [
    { title: appContext.title },
    { name: 'description', content: 'The Admin Console for khaleesi.ninja.' },
  ]
}


export default function Index(): JSX.Element {
  return (
    <div>New Frontend</div>
  )
}

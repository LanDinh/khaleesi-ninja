import type { MetaFunction, LinksFunction } from '@remix-run/node'
import { useContext } from 'react'
import { AppContext } from '../khaleesi/components/document'
import styles from '../khaleesi/styles/index.css'


// eslint-disable-next-line react-hooks/rules-of-hooks
export const meta: MetaFunction = () => {
  const appContext = useContext(AppContext)

  return [
    { title: appContext.title },
    { name: 'description', content: 'The Admin Console for khaleesi.ninja.' },
  ]
}

export const links: LinksFunction = () => [
  { rel: 'stylesheet', href: styles },
]


export default function Index(): JSX.Element {
  return (
    <div>New Frontend</div>
  )
}

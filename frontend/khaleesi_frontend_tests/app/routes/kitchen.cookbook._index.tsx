import type { MetaFunction } from '@remix-run/node'
import { useLoaderData } from 'react-router'
import type { khaleesi } from '../khaleesi/proto/proto'

export const meta: MetaFunction = () => {
  return [
    { title: 'khaleesi.ninja | Cookbook' },
    { name: 'description', content: 'Khaleesi\'s Dragonpit: a cookbook for hungry dragons.' },
  ]
}

export async function loader(): Promise<khaleesi.core.sawmill.EventsList> {
  const { SAWYER } = await import('../khaleesi/grpc/sawmill.server')
  return SAWYER.getEvents()
}

export default function RecipeIndex(): JSX.Element {
  useLoaderData<typeof loader>()

  return <div>
    Whatever
  </div>
}

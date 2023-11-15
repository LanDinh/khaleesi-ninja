import type { MetaFunction } from '@remix-run/node'
import { useLoaderData } from '@remix-run/react'
import { SAWYER } from '../khaleesi/grpc/clocktower'
import type { khaleesi } from '../khaleesi/proto/proto'

export const meta: MetaFunction = () => {
  return [
    { title: 'khaleesi.ninja | Cookbook' },
    { name: 'description', content: 'Khaleesi\'s Dragonpit: a cookbook for hungry dragons.' },
  ]
}

export async function loader(): Promise<khaleesi.core.sawmill.EventsList> {
  return SAWYER.getEvents()
}

export default function RecipeIndex(): JSX.Element {
  useLoaderData<typeof loader>()

  return <div>
    Whatever
  </div>
}

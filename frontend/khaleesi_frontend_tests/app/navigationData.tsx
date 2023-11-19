import type { NavigationElementProperties } from './khaleesi/navigation/navigationElement'
import { navigationProperties as kitchen } from './routes/kitchen'
import { navigationProperties as cookbook } from './routes/kitchen.cookbook'


export const navigationData: NavigationElementProperties[] = [
  { ...kitchen, children: [ cookbook ] },
]

export const iconLookup: { [id: string]: JSX.Element } = {
  'Test': <div>Test Icon</div>
}

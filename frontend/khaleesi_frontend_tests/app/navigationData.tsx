import type { NavigationElementProperties } from './khaleesi/navigation/navigationElement'
import { navigationProperties as home } from './khaleesi/navigation/navigationData'
import { navigationProperties as kitchen } from './routes/kitchen'
import { navigationProperties as cookbook } from './routes/kitchen.cookbook'


export const navigationData: NavigationElementProperties[] = [
  { ...home },
  { ...kitchen, children: [ cookbook ] },
]

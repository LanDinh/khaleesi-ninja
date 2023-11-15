import { HomeIcon } from '../components/icon'
import type { NavigationElementProperties } from './navigationElement'


export const topNavigationData: NavigationElementProperties[] = [
  {
    path : '/',
    label: 'Home',
    icon : <HomeIcon />,
  }
]
export const bottomNavigationData: NavigationElementProperties[] = [
  {
    path : '/profile',
    label: 'Profile',
    icon : <HomeIcon />,
  },
  {
    path : '/login',
    label: 'Login',
    icon : <HomeIcon />,
  }
]

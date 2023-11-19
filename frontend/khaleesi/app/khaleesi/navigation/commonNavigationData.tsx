import { HomeIcon } from '../home/icon'
import { LoginIcon, LogoutIcon } from '../auth/icon'
import type { NavigationElementProperties } from './navigationElement'


export const homeNavigationData: NavigationElementProperties = {
  path : '/',
  label: 'Home',
  icon : <HomeIcon />,
}
export const loginNavigationData: NavigationElementProperties = {
  path      : '/login',
  label     : 'Login',
  permission: 'anonymous',
  icon      : <LoginIcon />,
}
export const logoutNavigationData: NavigationElementProperties = {
  path      : '/logout',
  label     : 'Logout',
  permission: 'user',
  icon      : <LogoutIcon />,
}


export const topNavigationData: NavigationElementProperties[] = [
  homeNavigationData
]
export const bottomNavigationData: NavigationElementProperties[] = [
  loginNavigationData,
  logoutNavigationData,
]


export const iconLookup: { [id: string]: JSX.Element } = {
  'Home'  : <HomeIcon />,
  'Login' : <LoginIcon />,
  'Logout': <LogoutIcon />,
}

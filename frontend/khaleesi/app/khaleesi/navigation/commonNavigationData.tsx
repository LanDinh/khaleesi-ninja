import { HomeIcon } from '../home/icon'
import { LoginIcon, ProfileIcon } from '../auth/icon'
import type { NavigationElementProperties } from './navigationElement'


export const homeNavigationData: NavigationElementProperties = {
  path : '/',
  label: 'Home',
  icon : <HomeIcon />,
}
export const loginNavigationData: NavigationElementProperties = {
  path : '/login',
  label: 'Login',
  icon : <LoginIcon />,
}
export const profileNavigationData: NavigationElementProperties = {
  path : '/profile',
  label: 'Profile',
  icon : <ProfileIcon />,
}


export const topNavigationData: NavigationElementProperties[] = [
  homeNavigationData
]
export const bottomNavigationData: NavigationElementProperties[] = [
  loginNavigationData,
  profileNavigationData,
]

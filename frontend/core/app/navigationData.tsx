import { LoginIcon } from './khaleesi/components/icon'
import { KitchenIcon, BookIcon } from './components/icon'


export type NavigationElement = {
  path     : string,
  label    : string,
  icon     : JSX.Element,
  children?: NavigationElement[]
}

export const navigationData: NavigationElement[] = [
  {
    path    : 'kitchen',
    label   : 'Kitchen',
    icon    : <KitchenIcon />,
    children: [ { path: 'cookbook', label: 'Cookbook', icon: <BookIcon /> } ],
  },
  { path: 'login', label: 'Login', icon: <LoginIcon /> },
]
import type { RouteConfig } from '@remix-run/route-config'
import { route } from '@remix-run/route-config'

export const routes = [
  route('/login', 'khaleesi/auth/loginRoute.tsx'),
  route('/logout', 'khaleesi/auth/logoutRoute.tsx'),
] satisfies RouteConfig

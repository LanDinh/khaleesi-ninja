import type { RouteConfig } from '@react-router/dev/routes'
import { route } from '@react-router/dev/routes'

export const routes = [
  route('/login', 'khaleesi/auth/loginRoute.tsx'),
  route('/logout', 'khaleesi/auth/logoutRoute.tsx'),
] satisfies RouteConfig

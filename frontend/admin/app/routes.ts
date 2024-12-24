import type { RouteConfig } from '@react-router/dev/routes'
import { route } from '@react-router/dev/routes'
import { routes } from './khaleesi/routes'

export default [
  ...routes,
  route('/', 'home/indexRoute.tsx', { index: true }),
] satisfies RouteConfig

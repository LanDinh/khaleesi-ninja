import type { RouteConfig } from '@react-router/dev'
import { route } from '@react-router/dev'
import { routes } from './khaleesi/routes'

export default [
  ...routes,
  route('/', 'home/indexRoute.tsx', { index: true }),
] satisfies RouteConfig

import type { RouteConfig } from '@remix-run/route-config'
import { route } from '@remix-run/route-config'
import { routes } from './khaleesi/routes'

export default [
  ...routes,
  route('/', 'home/indexRoute.tsx', { index: true }),
] satisfies RouteConfig

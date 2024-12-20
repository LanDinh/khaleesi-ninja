import type { RouteConfig } from '@remix-run/route-config'
import { route } from '@remix-run/route-config'
import { routes } from './khaleesi/routes'

export default [
  ...routes,
  route('/kitchen', 'routes/kitchen.tsx'),
  route('/kitchen', 'routes/kitchen._index.tsx', { index: true }),
  route('/kitchen/cookbook', 'routes/kitchen.cookbook.tsx'),
  route('/kitchen/cookbook', 'routes/kitchen.cookbook._index.tsx', { index: true }),
] satisfies RouteConfig

import type { RouteConfig } from '@react-router/dev/routes'
import { route } from '@react-router/dev/routes'
import { routes } from './khaleesi/routes'

export default [
  ...routes,
  route('/kitchen', 'routes/kitchen.tsx'),
  route('/kitchen', 'routes/kitchen._index.tsx', { index: true }),
  route('/kitchen/cookbook', 'routes/kitchen.cookbook.tsx'),
  route('/kitchen/cookbook', 'routes/kitchen.cookbook._index.tsx', { index: true }),
] satisfies RouteConfig

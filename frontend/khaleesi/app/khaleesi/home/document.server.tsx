import type { LoaderFunctionArgs } from '@remix-run/node'
import { navigationData } from '../../navigationData'
import {
  topNavigationData,
  bottomNavigationData,
} from '../navigation/commonNavigationData'
import { Session } from '../auth/session.server'

export async function loader({ request }: LoaderFunctionArgs) {
  const session = new Session()
  await session.init(request)
  return {
    top    : topNavigationData.filter((data) => session.hasPermission(data.permission)),
    middle : navigationData.filter((data) => session.hasPermission(data.permission)),
    bottom : bottomNavigationData.filter((data) => session.hasPermission(data.permission)),
  }
}

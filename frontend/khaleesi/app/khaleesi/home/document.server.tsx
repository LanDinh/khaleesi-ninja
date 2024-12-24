import type { LoaderFunctionArgs } from 'react-router'
import { navigationData } from '../../navigationData'
import {
  topNavigationData,
  bottomNavigationData,
} from '../navigation/commonNavigationData'
import type { NavigationElementProperties } from '../navigation/navigationElement'
import { Session } from '../auth/session.server'

export async function loader(
    { request }: LoaderFunctionArgs,
): Promise<{
    top: NavigationElementProperties[],
    middle: NavigationElementProperties[],
    bottom: NavigationElementProperties[],
}> {
  const session = new Session()
  await session.init(request)
  return {
    top    : topNavigationData.filter((data) => session.hasPermission(data.permission)),
    middle : navigationData.filter((data) => session.hasPermission(data.permission)),
    bottom : bottomNavigationData.filter((data) => session.hasPermission(data.permission)),
  }
}

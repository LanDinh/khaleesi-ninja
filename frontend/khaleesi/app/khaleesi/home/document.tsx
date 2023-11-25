import { createContext, type Context, type PropsWithChildren } from 'react'
import type { LinksFunction, LoaderFunctionArgs } from '@remix-run/node'
import {
  Meta,
  Links as RemixLinks,
  Scripts,
  ScrollRestoration,
  Outlet,
  useLoaderData,
} from '@remix-run/react'
import { navigationData } from '../../navigationData'
import { breadcrumb, BreadCrumbs } from '../navigation/breadcrumb'
import { Navigation } from '../navigation/navigation'
import type { NavigationElementProperties } from '../navigation/navigationElement'
import { Content } from './content'
import { ErrorPage } from './error'
// @ts-ignore: styles have no types
import rootStyles from '../styles/root.css'
// @ts-ignore: styles have no types
import navigationStyles from '../styles/navigation.css'
// @ts-ignore: styles have no types
import tableStyles from '../styles/table.css'
import {
  homeNavigationData,
  topNavigationData,
  bottomNavigationData,
} from '../navigation/commonNavigationData'
import { Session } from '../auth/session.server'


export const handle = {
  ...breadcrumb(homeNavigationData),
}


export type AppContextType = {
  title     : string,
}
export const AppContext: Context<AppContextType> = createContext({
  title     : 'Change your title!',
})


type LoaderType = {
  top    : NavigationElementProperties[],
  middle : NavigationElementProperties[],
  bottom : NavigationElementProperties[],
}

export const loader = async ({ request }: LoaderFunctionArgs): Promise<LoaderType> => {
  const session = new Session()
  await session.init(request)
  return {
    top    : topNavigationData.filter((data) => session.hasPermission(data.permission)),
    middle : navigationData.filter((data) => session.hasPermission(data.permission)),
    bottom : bottomNavigationData.filter((data) => session.hasPermission(data.permission)),
  }
}

function Document({
  children,
  title,
  topNavigationData,
  middleNavigationData,
  bottomNavigationData,
}: PropsWithChildren<{
  title               : string,
  topNavigationData   : NavigationElementProperties[],
  middleNavigationData: NavigationElementProperties[],
  bottomNavigationData: NavigationElementProperties[],
}>): JSX.Element {
  return <html lang="en">
    <head>
      <meta charSet="utf-8" />
      <meta name="viewport" content="width=device-width,initial-scale=1" />
      <Meta />
      <RemixLinks />
    </head>
    <body>
    <div id="khaleesi-app">
      <div id="khaleesi-title" className="khaleesi-bar">{title}</div>
      <Navigation
        top={topNavigationData}
        middle={middleNavigationData}
        bottom={bottomNavigationData}
      />
      <BreadCrumbs />
      <Content>
        {children}
      </Content>
    </div>
      <ScrollRestoration />
      <Scripts />
    </body>
  </html>
}

export const links: LinksFunction = () => [
  // Font.
  { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Roboto&display=swap' },
  // Style.
  { rel: 'stylesheet', href: rootStyles },
  { rel: 'stylesheet', href: navigationStyles },
  { rel: 'stylesheet', href: tableStyles },
]

const filterAnonymous = (data: NavigationElementProperties): boolean => {
  if (!data) {
    return false
  }
  if (!data.permission) {
    return true
  }
  return 'anonymous' === data.permission
}

export function ErrorBoundary({ title }: { title: string }): JSX.Element {
  return <AppContext.Provider value={{ title: title }}>
    <Document
      title={title}
      topNavigationData={topNavigationData.filter(filterAnonymous)}
      middleNavigationData={navigationData.filter(filterAnonymous)}
      bottomNavigationData={bottomNavigationData.filter(filterAnonymous)}
    >
      <ErrorPage />
    </Document>
  </AppContext.Provider>
}

export function App({ title }: { title: string }): JSX.Element {
  const loaderData = useLoaderData() as LoaderType

  return <AppContext.Provider value={{ title: title }}>
    <Document
      title={title}
      topNavigationData={loaderData.top}
      middleNavigationData={loaderData.middle}
      bottomNavigationData={loaderData.bottom}
    >
      <Outlet />
    </Document>
  </AppContext.Provider>
}

import { createContext, useContext, type Context, type PropsWithChildren } from 'react'
import type { LinksFunction } from '@remix-run/node'
import { Meta, Links as RemixLinks, Scripts, ScrollRestoration, Outlet } from '@remix-run/react'
import { breadcrumb } from '../navigation/breadcrumb'
import { Navigation } from '../navigation/navigation'
import { Content } from './content'
import { ErrorPage } from './error'
// @ts-ignore: styles have no types
import styles from './index.css'
import { topNavigationData } from '../navigation/commonNavigationData'


export const handle = {
  ...breadcrumb(topNavigationData[0]),
}


export type AppContextType = {
  title: string,
}
export const AppContext: Context<AppContextType> = createContext({
  title: 'Change your title!'
})

function Document({ children }: PropsWithChildren<{}>): JSX.Element {
  const appContext: AppContextType = useContext(AppContext)

  return <html lang="en">
    <head>
      <meta charSet="utf-8" />
      <meta name="viewport" content="width=device-width,initial-scale=1" />
      <Meta />
      <RemixLinks />
    </head>
    <body>
      <div id="khaleesi-app">
        <div id="khaleesi-title" className="khaleesi-bar">{appContext.title}</div>
        <Navigation />
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
  { rel: 'stylesheet', href: styles },
]

export function ErrorBoundary({ title }: { title: string }): JSX.Element {
  return <AppContext.Provider value={{ title: title }}>
    <Document>
      <ErrorPage />
    </Document>
  </AppContext.Provider>
}

export function App({ title }: { title: string }): JSX.Element {
  return <AppContext.Provider value={{ title: title }}>
    <Document>
      <Outlet />
    </Document>
  </AppContext.Provider>
}

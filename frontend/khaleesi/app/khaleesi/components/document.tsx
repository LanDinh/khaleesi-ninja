import type { PropsWithChildren } from 'react'
import type { LinksFunction } from '@remix-run/node'
import { Meta, Links as RemixLinks, Scripts, ScrollRestoration, Outlet } from '@remix-run/react'
import { breadcrumb } from '../navigation/breadcrumb'
import { Navigation } from '../navigation/navigation'
import { Content } from './content'
import { ErrorPage } from './error'
// @ts-ignore: styles have no types
import rootStyles from '../styles/index.css'
// @ts-ignore: styles have no types
import navigationBarStyles from '../styles/navigation.css'
import { topNavigationData } from '../navigation/commonNavigationData'


export const handle = {
  ...breadcrumb(topNavigationData[0]),
}

function Document({ children, title }: PropsWithChildren<{ title: string }>): JSX.Element {
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
  { rel: 'stylesheet', href: rootStyles },
  { rel: 'stylesheet', href: navigationBarStyles },
]

export function ErrorBoundary({ title }: { title: string }): JSX.Element {
  return <Document title={title}>
    <ErrorPage />
  </Document>
}

export function App({ title }: { title: string }): JSX.Element {
  return <Document title={title}>
    <Outlet />
  </Document>
}

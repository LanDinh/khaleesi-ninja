import type { PropsWithChildren } from 'react'
import type { LinksFunction } from '@remix-run/node'
import { Meta, Links as RemixLinks, Scripts, ScrollRestoration, Outlet } from '@remix-run/react'
import { ErrorPage } from './error'
import styles from '../styles/index.css'


function Document({ children }: PropsWithChildren<{}>): JSX.Element {
  return <html lang="en">
    <head>
      <meta charSet="utf-8" />
      <meta name="viewport" content="width=device-width,initial-scale=1" />
      <Meta />
      <RemixLinks />
    </head>
    <body>
      { children }
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

export function ErrorBoundary(): JSX.Element {
  return <Document>
    <ErrorPage />
  </Document>
}

export function App(): JSX.Element {
  return <Document>
    <Outlet />
  </Document>
}

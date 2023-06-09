import type { PropsWithChildren } from 'react'
import type { LinksFunction } from '@remix-run/node'
import { Meta, Links as RemixLinks, Scripts, ScrollRestoration } from '@remix-run/react'
import styles from '../styles/index.css'


export const Links: LinksFunction = () => [
  // Font.
  { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Roboto&display=swap' },
  // Style.
  { rel: 'stylesheet', href: styles },
]


export function Document({ children }: PropsWithChildren<{}>): JSX.Element {
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
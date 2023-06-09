import type { LinksFunction } from '@remix-run/node'
import { useRouteError, isRouteErrorResponse } from '@remix-run/react'
import {
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
} from '@remix-run/react'
import styles from '../khaleesi/styles/index.css'


export const links: LinksFunction = () => [
  // Font.
  { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Roboto&display=swap' },
  // Style.
  { rel: 'stylesheet', href: styles },
]
export function ErrorBoundary() {
  const error = useRouteError()

  if (isRouteErrorResponse(error)) {
    return <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width,initial-scale=1" />
        <Meta />
        <Links />
      </head>
      <body>
        <h1>{ error.status }</h1>
        <div>{ error.statusText }</div>
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  }

  const errorMessage = error instanceof Error ? error.message : 'Unknown error'
  return <html lang="en">
    <head>
      <meta charSet="utf-8" />
      <meta name="viewport" content="width=device-width,initial-scale=1" />
      <Meta />
      <Links />
    </head>
    <body>
      <div>An error happened: { errorMessage }</div>
      <ScrollRestoration />
      <Scripts />
    </body>
  </html>
}

export default function App() {
  return <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width,initial-scale=1" />
        <Meta />
        <Links />
      </head>
      <body>
        <Outlet />
        <ScrollRestoration />
        <Scripts />
      </body>
  </html>
}

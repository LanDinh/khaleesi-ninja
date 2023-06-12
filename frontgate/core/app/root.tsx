import { useRouteError } from '@remix-run/react'
import { Outlet } from '@remix-run/react'
import { Document, Links } from './khaleesi/components/document'
import { ErrorPage } from './khaleesi/components/error'


export const links = Links

export function ErrorBoundary() {
  const error = useRouteError()

  return <Document>
    <ErrorPage error={error} />
  </Document>
}

export default function App() {
  return <Document>
    <Outlet />
  </Document>
}

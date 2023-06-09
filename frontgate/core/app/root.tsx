import { useRouteError, isRouteErrorResponse } from '@remix-run/react'
import { Outlet } from '@remix-run/react'
import { Document, Links } from './khaleesi/components/document'


export const links = Links

export function ErrorBoundary() {
  const error = useRouteError()

  if (isRouteErrorResponse(error)) {
    return <Document>
      <h1>{ error.status }</h1>
      <div>{ error.statusText }</div>
    </Document>
  }

  const errorMessage = error instanceof Error ? error.message : 'Unknown error'
  return <Document>
    <div>An error happened: { errorMessage }</div>
  </Document>
}

export default function App() {
  return <Document>
    <Outlet />
  </Document>
}

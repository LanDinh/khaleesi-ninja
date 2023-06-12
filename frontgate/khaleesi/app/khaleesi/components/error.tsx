import { isRouteErrorResponse } from '@remix-run/react'


export function ErrorPage(error: any): JSX.Element {

  let errorTitle = 'Woops! Some dragon went crazy...'
  let errorMessage = error instanceof Error ? error.message : 'Try again later.'

  if (isRouteErrorResponse(error)) {
    errorTitle = `HTTP ${error.status}`
    errorMessage = error.statusText
  }

  return <main>
    <h1>{ errorTitle }</h1>
    <div>{ errorMessage }</div>
  </main>
}
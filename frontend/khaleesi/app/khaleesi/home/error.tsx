import { isRouteErrorResponse, useRouteError } from '@remix-run/react'


export function ErrorPage(): JSX.Element {
  const error = useRouteError()

  let errorTitle = 'Woops! Some dragon went crazy...'
  let errorMessage = 'Try again later.'
  if (error instanceof Error) {
    errorMessage = error.message
    if (process.env.NODE_ENV && error.stack) {
      errorMessage = error.stack
    }
  }

  if (isRouteErrorResponse(error)) {
    errorTitle = `HTTP ${error.status}`
    errorMessage = error.statusText
  }

  return <>
    <h1>{ errorTitle }</h1>,
    <div>{ errorMessage }</div>,
  </>
}
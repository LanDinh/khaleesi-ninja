import type { HydrationState, InitialEntry } from '@remix-run/router'
import type { UNSAFE_FutureConfig as FutureConfig } from '@remix-run/react'
import { unstable_createRemixStub } from '@remix-run/testing'


type RemixStubOptions = {
  initialEntries?   : InitialEntry[]
  hydrationData?    : HydrationState
  initialIndex?     : number
  remixConfigFuture?: Partial<FutureConfig>
}
export function createRemixStub(
  element  : JSX.Element,
  childText: string = '',
): (options: RemixStubOptions) => JSX.Element {
  const children = []
  if (0 < childText.length) {
    children.push({ path: '/', element: <div>{childText}</div> })
  }

  return unstable_createRemixStub([{
    path    : '/',
    element : element,
    children: children,
  }])
}
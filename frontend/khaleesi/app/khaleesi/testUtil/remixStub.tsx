import type { HydrationState, InitialEntry } from '@remix-run/router'
import type { UNSAFE_FutureConfig as FutureConfig } from '@remix-run/react'
import { createRemixStub } from '@remix-run/testing'
import type React from 'react'


type RemixStubOptions = {
  initialEntries?   : InitialEntry[]
  hydrationData?    : HydrationState
  initialIndex?     : number
  remixConfigFuture?: Partial<FutureConfig>
}
export function createTestingStub(
  element: React.ComponentType,
  path   : string = '/',
): (options: RemixStubOptions) => JSX.Element {
  return createRemixStub([{ path: path, Component: element }])
}
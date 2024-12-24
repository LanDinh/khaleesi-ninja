import { createRoutesStub } from 'react-router'
import type { RoutesTestStubProps } from 'react-router'
import type React from 'react'


export function createTestingStub(
  element: React.ComponentType,
  path   : string = '/',
): (options: RoutesTestStubProps) => JSX.Element {
  return createRoutesStub([{ path: path, Component: element }])
}

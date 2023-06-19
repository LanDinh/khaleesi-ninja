import type { PropsWithChildren } from 'react'
import { BreadCrumbs } from './navigation/breadcrumb'


export function Content({ children }: PropsWithChildren<{}>): JSX.Element {
  return <main id="khaleesi-content">
    <BreadCrumbs />
    {children}
  </main>
}
import type { PropsWithChildren } from 'react'


export function Content({ children }: PropsWithChildren<unknown>): JSX.Element {
  return <main id="khaleesi-content">
    {children}
  </main>
}
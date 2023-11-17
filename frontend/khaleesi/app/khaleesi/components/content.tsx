import type { PropsWithChildren } from 'react'


export function Content({ children }: PropsWithChildren<{}>): JSX.Element {
  return <main id="khaleesi-content">
    {children}
  </main>
}
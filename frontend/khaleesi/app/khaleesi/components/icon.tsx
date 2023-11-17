import type { PropsWithChildren } from 'react'


export type IconProperties = {
  id?       : string
  className?: string
}

type IconInternalProperties = IconProperties & {
  viewBox?: string
}


export function Icon({
  viewBox = '0 0 24 24',
  children,
  ...props
}: PropsWithChildren<IconInternalProperties>): JSX.Element {
  return <svg
    className="icon"
    xmlns="http://www.w3.org/2000/svg"
    viewBox={viewBox}
    fill="currentcolor"
    role="icon"
    {...props}
  >
    {children}
  </svg>
}

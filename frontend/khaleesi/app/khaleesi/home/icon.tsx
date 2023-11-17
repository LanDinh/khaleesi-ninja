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

export function MenuIcon(props: IconProperties): JSX.Element {
  return <Icon {...props}>
    <path d="M0 0h24v24H0V0z" fill="none"/>
    <path d="M4 18h16c.55 0 1-.45 1-1s-.45-1-1-1H4c-.55 0-1 .45-1 1s.45 1 1 1zm0-5h16c.55 0 1-.45 1-1s-.45-1-1-1H4c-.55 0-1 .45-1 1s.45 1 1 1zM3 7c0 .55.45 1 1 1h16c.55 0 1-.45 1-1s-.45-1-1-1H4c-.55 0-1 .45-1 1z"/>
  </Icon>
}

export function SettingsIcon(props: IconProperties): JSX.Element {
  return <Icon {...props}>
    <rect fill="none" height="24" width="24"/>
    <path d="M19.5,12c0-0.23-0.01-0.45-0.03-0.68l1.86-1.41c0.4-0.3,0.51-0.86,0.26-1.3l-1.87-3.23c-0.25-0.44-0.79-0.62-1.25-0.42 l-2.15,0.91c-0.37-0.26-0.76-0.49-1.17-0.68l-0.29-2.31C14.8,2.38,14.37,2,13.87,2h-3.73C9.63,2,9.2,2.38,9.14,2.88L8.85,5.19 c-0.41,0.19-0.8,0.42-1.17,0.68L5.53,4.96c-0.46-0.2-1-0.02-1.25,0.42L2.41,8.62c-0.25,0.44-0.14,0.99,0.26,1.3l1.86,1.41 C4.51,11.55,4.5,11.77,4.5,12s0.01,0.45,0.03,0.68l-1.86,1.41c-0.4,0.3-0.51,0.86-0.26,1.3l1.87,3.23c0.25,0.44,0.79,0.62,1.25,0.42 l2.15-0.91c0.37,0.26,0.76,0.49,1.17,0.68l0.29,2.31C9.2,21.62,9.63,22,10.13,22h3.73c0.5,0,0.93-0.38,0.99-0.88l0.29-2.31 c0.41-0.19,0.8-0.42,1.17-0.68l2.15,0.91c0.46,0.2,1,0.02,1.25-0.42l1.87-3.23c0.25-0.44,0.14-0.99-0.26-1.3l-1.86-1.41 C19.49,12.45,19.5,12.23,19.5,12z M12.04,15.5c-1.93,0-3.5-1.57-3.5-3.5s1.57-3.5,3.5-3.5s3.5,1.57,3.5,3.5S13.97,15.5,12.04,15.5z"/>
  </Icon>
}
export function LoginIcon(props: IconProperties): JSX.Element {
  return <Icon {...props}>
    <g><rect fill="none" height="24" width="24"/></g>
    <g><path d="M10.3,7.7L10.3,7.7c-0.39,0.39-0.39,1.01,0,1.4l1.9,1.9H3c-0.55,0-1,0.45-1,1v0c0,0.55,0.45,1,1,1h9.2l-1.9,1.9 c-0.39,0.39-0.39,1.01,0,1.4l0,0c0.39,0.39,1.01,0.39,1.4,0l3.59-3.59c0.39-0.39,0.39-1.02,0-1.41L11.7,7.7 C11.31,7.31,10.69,7.31,10.3,7.7z M20,19h-7c-0.55,0-1,0.45-1,1v0c0,0.55,0.45,1,1,1h7c1.1,0,2-0.9,2-2V5c0-1.1-0.9-2-2-2h-7 c-0.55,0-1,0.45-1,1v0c0,0.55,0.45,1,1,1h7V19z"/></g>
  </Icon>
}
export function HomeIcon(props: IconProperties): JSX.Element {
  return <Icon viewBox="0 -960 960 960" {...props}>
    <path d="M220-180h150v-250h220v250h150v-390L480-765 220-570v390Zm0 60q-24.75 0-42.375-17.625T160-180v-390q0-14.25 6.375-27T184-618l260-195q8.295-6 17.344-9 9.049-3 18.853-3 9.803 0 18.717 3 8.915 3 17.086 9l260 195q11.25 8.25 17.625 21T800-570v390q0 24.75-17.625 42.375T740-120H530v-250H430v250H220Zm260-353Z"/>
  </Icon>
}

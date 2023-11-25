import { Icon, type IconProperties } from '../icon'


export function FirstIcon(props: IconProperties): JSX.Element {
  return <Icon viewBox="0 -960 960 960" {...props}>
    <path d="M280-240q-17 0-28.5-11.5T240-280v-400q0-17 11.5-28.5T280-720q17 0 28.5 11.5T320-680v400q0 17-11.5 28.5T280-240Zm272-240 156 156q11 11 11 28t-11 28q-11 11-28 11t-28-11L468-452q-6-6-8.5-13t-2.5-15q0-8 2.5-15t8.5-13l184-184q11-11 28-11t28 11q11 11 11 28t-11 28L552-480Z"/>
  </Icon>
}

export function PreviousIcon(props: IconProperties): JSX.Element {
  return <Icon viewBox="0 -960 960 960" {...props}>
    <path d="m432-480 156 156q11 11 11 28t-11 28q-11 11-28 11t-28-11L348-452q-6-6-8.5-13t-2.5-15q0-8 2.5-15t8.5-13l184-184q11-11 28-11t28 11q11 11 11 28t-11 28L432-480Z"/>
  </Icon>
}

export function NextIcon(props: IconProperties): JSX.Element {
  return <Icon viewBox="0 -960 960 960" {...props}>
    <path d="M504-480 348-636q-11-11-11-28t11-28q11-11 28-11t28 11l184 184q6 6 8.5 13t2.5 15q0 8-2.5 15t-8.5 13L404-268q-11 11-28 11t-28-11q-11-11-11-28t11-28l156-156Z"/>
  </Icon>
}

export function LastIcon(props: IconProperties): JSX.Element {
  return <Icon viewBox="0 -960 960 960" {...props}>
    <path d="M408-480 252-636q-11-11-11-28t11-28q11-11 28-11t28 11l184 184q6 6 8.5 13t2.5 15q0 8-2.5 15t-8.5 13L308-268q-11 11-28 11t-28-11q-11-11-11-28t11-28l156-156Zm272-240q17 0 28.5 11.5T720-680v400q0 17-11.5 28.5T680-240q-17 0-28.5-11.5T640-280v-400q0-17 11.5-28.5T680-720Z"/>
  </Icon>
}

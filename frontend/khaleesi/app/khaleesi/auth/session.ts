import {
  createCookieSessionStorage,
  redirect,
  json,
  type Session,
  type TypedResponse,
} from '@remix-run/node'


const sessionSecret = 'shouldBeSetByBackend'

export const { getSession, commitSession, destroySession } = createCookieSessionStorage({
  cookie: {
    name    : 'khaleesi_session',
    //domain  : process.env.KHALEESI_DOMAIN,
    secure  : true,
    secrets : [sessionSecret],
    sameSite: 'lax',
    path    : '/',
    maxAge  : 60 * 60 * 24 * 30,  // 30d.
    httpOnly: true,
  },
})

export async function createUserSession(
  sessionId: string,
  redirectTo: string,
  ): Promise<TypedResponse<never>> {
  const session = await getSession()
  session.set('sessionId', sessionId)
  session.set('permission', sessionId)
  return redirect(redirectTo, { headers: { 'Set-Cookie': await commitSession(session) } })
}

export async function getSessionData(
  request: Request,
  permissionName: string = '',
): Promise<TypedResponse<{ permission: boolean, session: Session }>> {
  const session = await getSession(request.headers.get('Cookie'))
  if (!session.has('permission')) {
    return json({ permission: false, session: session })
  }
  return json({ permission: session.get('permission') === permissionName, session: session })
}

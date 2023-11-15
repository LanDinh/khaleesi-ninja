import type { TypedResponse } from '@remix-run/node'
import {
  createCookieSessionStorage,
  redirect,
} from '@remix-run/node'


const sessionSecret = 'shouldBeSetByBackend'

const storage = createCookieSessionStorage({
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
  const session = await storage.getSession()
  session.set('sessionId', sessionId)
  console.log('session set')
  return redirect(redirectTo, { headers: { 'Set-Cookie': await storage.commitSession(session) } })
}

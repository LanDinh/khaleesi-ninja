import type { UNSAFE_DataWithResponseInit, Session as RemixSession } from 'react-router'
import {
  createCookieSessionStorage,
  redirectDocument,
  redirect,
  data,
} from 'react-router'


const sessionSecret = 'shouldBeSetByBackend'


const { getSession, commitSession, destroySession } = createCookieSessionStorage({
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



export class Session {

  remixSession?: RemixSession
  initialized  : boolean
  authenticated: boolean

  constructor() {
    this.initialized   = false
    this.authenticated = false
  }

  async init(request: Request): Promise<void> {
    this.remixSession  = await getSession(request.headers.get('Cookie'))
    this.initialized   = true
    this.authenticated = this.remixSession!.has('permission')
  }

  async create(
    sessionId : string,
    redirectTo: string,
  ): Promise<Response | UNSAFE_DataWithResponseInit<{ message: string }>> {
    if (!this.initialized) {
      return data({ message: 'No session available yet!' })
    }
    this.remixSession!.set('sessionId', sessionId)
    this.remixSession!.set('permission', sessionId)
    return redirectDocument(
      redirectTo,
      { headers: { 'Set-Cookie': await commitSession(this.remixSession!) } },
    )
  }

  async destroy(
      redirectTo: string,
  ): Promise<Response | UNSAFE_DataWithResponseInit<{ message: string }>> {
    if (this.initialized) {
      this.initialized   = false
      this.authenticated = false
      return redirectDocument(
        redirectTo,
        { headers: { 'Set-Cookie': await destroySession(this.remixSession!) } },
      )
    }
    return redirectDocument(redirectTo)
  }

  hasPermission(permission: string = ''): boolean {
    if ('' === permission) {
      // No permission required.
      return true
    }
    if (!this.initialized || !this.authenticated) {
      // No session created, or anonymous. Treat as anonymous.
      return 'anonymous' === permission
    }
    if (!this.remixSession!.has('permission')) {
      // User has no permissions.
      return false
    }
    return this.remixSession!.get('permission') === permission
  }

  requirePermission(permission: string = ''): void {
    if (!this.hasPermission(permission)) {
      if (!this.authenticated) {
        throw redirect('/login')
      }
      throw data({ message: 'Permission denied.' }, { status: 403 })
    }
  }
}

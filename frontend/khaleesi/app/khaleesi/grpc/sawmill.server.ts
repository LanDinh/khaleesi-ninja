import type { khaleesi } from '../proto/proto'
import { Singleton, Client } from './util.server'


class Sawyer extends Client<khaleesi.core.sawmill.Sawyer> {
  constructor() {
    super('core', 'sawmill', 'Sawyer')
  }

  async getEvents(): Promise<khaleesi.core.sawmill.EventsList> {
    return await this.stub.getEvents({})
  }
}

export const SAWYER = Singleton('core', 'sawmill', () => new Sawyer())

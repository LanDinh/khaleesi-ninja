import type { khaleesi } from '../proto/proto'
import { Client } from './util'


class Sawyer extends Client<khaleesi.core.sawmill.Sawyer> {
  constructor() {
    super('core', 'sawmill', 'Sawyer')
  }

  async getEvents(): Promise<khaleesi.core.sawmill.EventsList> {
    return this.stub.getEvents({}).then((response) => {
      console.log(response)
      return response
    })
  }
}

export const SAWYER = new Sawyer()

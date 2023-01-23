import * as cache from '@actions/cache'
import * as dockerCli from 'docker-cli-js'

export async function runAction(image, commit) {
  const key = `khaleesi/${commit}/images/${image}`
  const path = `/tmp/${key}`

  await cache.restoreCache([ path ], key, [])

  const docker = new dockerCli.Docker()
  await docker.command(`load -i ${path}`)
}

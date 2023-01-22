import * as cache from '@actions/cache'
import * as dockerCli from 'docker-cli-js'

export async function runAction(image) {
  const path = `/tmp/khaleesi/images/${image}`
  const key = `khaleesi/images/${image}`
  await cache.restoreCache([path], key, [])

  const docker = new dockerCli.Docker()

  await docker.command(`load -i ${path}`)
}

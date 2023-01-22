const cache = require('@actions/cache')
const dockerCli = require('docker-cli-js')

export async function runAction(image) {
  const path = `/tmp/khaleesi/images/${image}`
  const key = `khaleesi/images/${image}`
  await cache.restoreCache([path], key, [])

  const docker = dockerCli.Docker()

  await docker.command(`load -i ${path}`)
}

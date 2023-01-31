// noinspection JSUnresolvedFunction,NpmUsedModulesInstalled

import * as core from '@actions/core'
import * as cache from '@actions/cache'
import * as dockerCli from 'docker-cli-js'
import * as fs from 'fs'


const image = core.getInput('image')
const commit = core.getInput('commit')


export async function runAction(image, commit) {
  const key = `khaleesi/${commit}/images/${image}`
  const path = `/tmp/${key}`
  const path_directory = path.split('/').slice(0, -1).join('/')

  fs.mkdirSync(path_directory, { recursive: true })

  const docker = new dockerCli.Docker()
  await docker.command(`save -o ${path} ${image}`)

  await cache.saveCache([ path ], key, [])
}


runAction(image, commit)
    .then(() => console.log('Finished saving the image.'))
    .catch((error) => core.setFailed(error.message))

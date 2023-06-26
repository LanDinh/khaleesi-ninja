// noinspection JSUnresolvedFunction,JSUnresolvedVariable,NpmUsedModulesInstalled

import * as core from '@actions/core'
import * as loadImage from '../load-image/action.js'

async function runAction() {
  const services = JSON.parse(core.getInput('services'))
  const containerMode = core.getInput('containerMode')
  const commit = core.getInput('commit')
  for (const service of services){
    const image = `khaleesi-ninja/${service.gate}/${service.name}:latest-${containerMode}`
    await loadImage.runAction(image, commit)
  }
}

runAction()
    .then(() => console.log('Finished loading all images.'))
    .catch((error) => core.setFailed(error.message))

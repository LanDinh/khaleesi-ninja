import * as core from '@actions/core'
import * as loadImage from '../load-image/action.js'

async function runAction() {
  const services = core.getInput('services')
  const container_mode = core.getInput('container_mode')
  const commit = core.getInput('commit')
  for (const service of services){
    const image = `khaleesi-ninja/${service.gate}/${service.name}:latest-${container_mode}`
    await loadImage.runAction(image, commit)
  }
}

runAction()
    .then(() => console.log('Finished loading all images.'))
    .catch((error) => core.setFailed(error.message))

// noinspection JSUnresolvedFunction,JSUnresolvedVariable,NpmUsedModulesInstalled

import * as core from '@actions/core'
import * as loadImage from '../load-image/action.js'

async function runAction() {
  const apps = JSON.parse(core.getInput('apps'))
  const containerMode = core.getInput('containerMode')
  const commit = core.getInput('commit')
  for (const app of apps){
    const image = `khaleesi-ninja/${app.site}/${app.name}:latest-${containerMode}`
    await loadImage.runAction(image, commit)
  }
}

runAction()
    .then(() => console.log('Finished loading all images.'))
    .catch((error) => core.setFailed(error.message))

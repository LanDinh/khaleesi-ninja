// noinspection JSUnresolvedFunction,NpmUsedModulesInstalled

import * as core from '@actions/core'
import { runAction } from './action.js'


const image = core.getInput('image')
const commit = core.getInput('commit')


runAction(image, commit)
    .then(() => console.log('Finished loading the image.'))
    .catch((error) => core.setFailed(error.message))

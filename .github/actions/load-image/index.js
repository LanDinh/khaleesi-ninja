import * as core from '@actions/core'
import { action } from './action.js'


const image = core.getInput('image')
action.runAction(image)
    .then(() => console.log('Finished loading the image.'))
    .catch((error) => core.setFailed(error.message))

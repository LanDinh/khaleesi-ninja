import * as core from '@actions/core'
import { runAction } from './action.js'


const image = core.getInput('image')
runAction(image)
    .then(() => console.log('Finished loading the image.'))
    .catch((error) => core.setFailed(error.message))

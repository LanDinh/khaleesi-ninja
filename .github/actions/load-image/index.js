const core = require('@actions/core')
const action = require('./action')


const image = core.getInput('image')
action.runAction(image)
    .then(() => console.log('Finished loading the image.'))
    .catch((error) => core.setFailed(error.message))

const core = require('@actions/core');
const cache = require('@actions/cache');
const { docker } = require('docker-cli-js');

try {
  const image = core.getInput('image');
  const path = `/tmp/khaleesi/images/${image}`
  const key = `khaleesi/images/${image}`
  await cache.restoreCache([ path ], key, [])
  await docker(`load -i ${path}`)
} catch (error) {
  core.setFailed(error.message);
}
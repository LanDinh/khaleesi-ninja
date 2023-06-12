// noinspection JSUnresolvedReference
/** @type {import('eslint').Linter.Config} */
module.exports = {
  extends: [ "@remix-run/eslint-config", "@remix-run/eslint-config/node" ],
  ignorePatterns: [ "/app/khaleesi/proto/*.d.ts" ],
  rules: {
    "semi": [ 2, "never" ],
    "quotes": [ 2, "single" ],
    "object-curly-spacing": [ 2, "always" ],
    "@typescript-eslint/explicit-function-return-type": 2
  }
}

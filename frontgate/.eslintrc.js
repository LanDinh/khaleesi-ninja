// noinspection JSUnresolvedReference
/** @type {import('eslint').Linter.Config} */
module.exports = {
  extends: [ "@remix-run/eslint-config", "@remix-run/eslint-config/node" ],
  ignorePatterns: [ "/app/khaleesi/proto/*.d.ts" ],
  rules: {
    "max-len": [2, { code: 100, tabWidth: 2, ignorePattern: "\\s*<path" }],
    "object-curly-spacing": [ 2, "always" ],
    "quotes": [ 2, "single" ],
    "semi": [ 2, "never" ],
    "@typescript-eslint/explicit-function-return-type": 2
  }
}

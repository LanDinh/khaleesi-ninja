// noinspection JSUnresolvedReference
/** @type {import('eslint').Linter.Config} */
module.exports = {
  extends: [ "eslint:recommended" ],
  overrides: [
    {
      files: ["**/*.{js,jsx,ts,tsx}"],
      extends: [
        "plugin:react/recommended",
        "plugin:react/jsx-runtime",
        "plugin:react-hooks/recommended",
        "plugin:jsx-a11y/recommended",
      ],
      rules: {
        "jsx-a11y/aria-role": [2, { "allowedInvalidRoles": ["icon"] }]
      }
    },
    {
      files: ["**/*.{ts,tsx}"],
      extends: [
        "plugin:@typescript-eslint/recommended",
        "plugin:import/recommended",
        "plugin:import/typescript",
      ],
    }
  ],
  ignorePatterns: [ "/app/khaleesi/proto/*.d.ts" ],
  rules: {
    "max-len": [2, { code: 100, tabWidth: 2, ignorePattern: "\\s*<path", ignoreUrls: true }],
    "object-curly-spacing": [ 2, "always" ],
    "quotes": [ 2, "single" ],
    "semi": [ 2, "never" ],
    "@typescript-eslint/explicit-function-return-type": 2
  }
}

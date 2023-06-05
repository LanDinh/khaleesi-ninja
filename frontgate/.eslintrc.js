/** @type {import('eslint').Linter.Config} */
module.exports = {
  extends: ["@remix-run/eslint-config", "@remix-run/eslint-config/node"],
  ignorePatterns: ["/app/core/proto/*.d.ts"],
  rules: {
    "semi": [2, "never"]
  }
};

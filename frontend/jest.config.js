// noinspection JSUnresolvedReference
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  transform: {
    '^.+\\.tsx?$': 'ts-jest',
  },
  transformIgnorePatterns: ['node_modules/'],
  collectCoverage: true,
  coverageReporters: [
    [ 'lcovonly', { projectRoot: '../..' } ]
  ],
  coveragePathIgnorePatterns: [ 'tests' ],
  moduleNameMapper: {
    '\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$':
        '<rootDir>/tests/mocks/fileMock.ts',
    '\\.(css)$': '<rootDir>/tests/mocks/styleMock.ts',
  },
}
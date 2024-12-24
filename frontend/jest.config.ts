import type { Config } from 'jest'

export default {
  preset: 'ts-jest',
  testEnvironment: './app/khaleesi/testUtil/attachFetchApi.ts',
  transform: {
    '^.+\\.tsx?$': 'ts-jest',
  },
  transformIgnorePatterns: ['node_modules/'],
  collectCoverage: true,
  coverageReporters: [
    [ 'lcovonly', { projectRoot: '../..' } ]
  ],
  coveragePathIgnorePatterns: [ '[^/]*/tests/.*' ],
  moduleNameMapper: {
    '\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$':
        '<rootDir>/tests/mocks/fileMock.ts',
    '\\.(css\\?url)$': '<rootDir>/tests/mocks/styleMock.ts',
    '^@web3-storage/multipart-parser$': require.resolve('@web3-storage/multipart-parser'),
  },
  testMatch: [ "**/tests/**/test*.ts?(x)" ]
} satisfies Config

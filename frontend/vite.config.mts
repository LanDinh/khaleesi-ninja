// noinspection JSUnresolvedReference
import { reactRouter } from '@react-router/dev/vite'
import { defineConfig } from 'vite'


export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 8000,
  },
  plugins: [reactRouter()],
})

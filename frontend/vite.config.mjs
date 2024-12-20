// noinspection JSUnresolvedReference
import { vitePlugin as remix } from '@remix-run/dev';
import { defineConfig } from 'vite';
export default defineConfig({
    server: {
        host: '0.0.0.0',
        port: 8000,
    },
    plugins: [remix({
            ignoredRouteFiles: ['**/.*'],
            // appDirectory: 'app',
            // assetsBuildDirectory: 'public/build',
            // serverBuildPath: 'build/index.js',
            // publicPath: 'build/',
            future: {
                v3_fetcherPersist: true,
                v3_relativeSplatPath: true,
                v3_throwAbortReason: true,
                v3_lazyRouteDiscovery: true,
                v3_singleFetch: true,
                v3_routeConfig: true,
            },
        })],
});

import path from 'node:path'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx';
import AppLoading from 'vite-plugin-app-loading'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import VueRouter from 'unplugin-vue-router/vite'
import { VueRouterAutoImports } from 'unplugin-vue-router'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())
  console.log(env)
  return {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
        '#': path.resolve(__dirname, 'api'),
      },
    },
    // 构建选项 https://cn.vitejs.dev/config/build-options
    build: {
      outDir: mode === 'production' ? 'dist' : `dist-${mode}`,
      sourcemap: env.VITE_BUILD_SOURCEMAP === 'true',
    },
    server: {
      // open: true,
      host: true,
      port: 7878,
      proxy: {
        '/api': {
          target: env.VITE_BACKEND_ENDPOINT,
          changeOrigin: true,
          // rewrite: path => path.replace(/\/proxy/, ''),
        },
        '/file': {
          target: env.VITE_OSS_ENDPOINT,
          changeOrigin: true,
          rewrite: path => path.replace(/\/file/, ''),
        }
      },
    },
    plugins:
      [
        tailwindcss(),
        VueRouter({
          dts: './src/types/router.d.ts',
          routesFolder: ['src/views'],
          exclude: [
            '**/components/**/*.vue',
            '**/components/*.vue',
          ],
          routeBlockLang: 'yaml'
        }),
        vue(),
        vueJsx(),
        AutoImport({
          imports: [
            'vue', 'pinia', VueRouterAutoImports,
          ],
          resolvers: [ElementPlusResolver()],
          dts: './src/types/auto-import.d.ts',
        }),
        Components({
          resolvers: [ElementPlusResolver()],
          globs: [
            'src/components/**'
          ],
          dts: './src/types/components.d.ts',
        }),
        AppLoading('loading.html'),
      ],
  }
})

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

import 'element-plus/dist/index.css'
import './style.css'
import App from './App.vue'
import "@/utils/refreshTokenInterceptor"

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

createApp(App)
    .use(pinia)
    .use(router)
    .mount('#app')

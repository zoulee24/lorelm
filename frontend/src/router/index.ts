import { createRouter, createWebHashHistory } from "vue-router";
import { loadingFadeOut } from 'virtual:app-loading'

import { routes, handleHotUpdate } from 'vue-router/auto-routes'
import { setupRoutes } from "./guards";

const router = createRouter({
  history: createWebHashHistory(),
  // routes: useSettingsStore(pinia).settings.app.routeBaseOn === 'filesystem' ? constantRoutesByFilesystem : constantRoutes,
  routes,
})

if (import.meta.hot) {
  handleHotUpdate(router)
}

setupRoutes(router)

router.isReady().then(() => {
  loadingFadeOut()
})

export default router
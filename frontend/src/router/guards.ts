import useUserStore from "@/store/user";
import type { Router } from "vue-router";

export const setupRoutes = (router: Router) => {
  router.beforeEach(async (to, _, next) => {
    const userStore = useUserStore()
    // // console.log(userStore.token, userStore.user);

    if (!userStore.isLogined) {
      // 如果是登录页或注册页，直接放行
      if (to.name === 'Login' || to.name === 'Register') {
        next()
      } else {
        // 其他页面跳转到登录页，并携带redirect参数
        next({
          name: 'Login',
          query: {
            redirect: to.fullPath ?? '/',
          },
        })
      }
    } else {
      next()
    }
  })
}


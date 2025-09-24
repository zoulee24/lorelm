import { defineStore } from "pinia";
import { computed, nextTick, ref } from "vue";

import type { JwtToken } from "@/schemas/base";
import type { UserResponse, UserLoginForm } from "@/schemas/admin";
import userApi from "@/api/admin/user";

const useUserStore = defineStore("user", () => {
  const token = ref<JwtToken>()
  const user = ref<UserResponse>()

  // watch(token, async (newVal, oldVal) => {
  //   if (newVal && !oldVal) {
  //     await freshUserInfo()
  //   }
  // })

  // const user_permission = computed(() =>
  //   new Set(user.value?.roles.map(role => role.permissions).flat() || []))
  // const user_permission_head = computed(() =>
  //   // 按照:拆分为两个取前面
  //   new Set(user.value?.roles.map(role => role.permissions).flat().map(it => it.split('.', 2)[0]) || []))
  // // 对比 permission
  // const compare_permission = (permissions: string[] | string, one?: boolean): boolean => {
  //   if (!user.value) return false
  //   // 如果是 字符串就转换成数组
  //   const permissionList = typeof permissions === "string" ? [permissions] : permissions;

  //   // 如果是任一匹配模式
  //   const compare_func = (perm: string) => {
  //     // 判断有没有:
  //     const head = perm.split(".", 2).length == 1;
  //     // 如果有:，判断是否包含，如果没有判断有没有以这个开头的
  //     return head
  //       ? user_permission_head.value.has(perm)
  //       : user_permission.value.has(perm)
  //   }
  //   // // 全匹配模式：确保所有权限都存在
  //   // console.log(permissionList, one, user_permission.value, permissionList.some(compare_func), permissionList.every(compare_func))
  //   return one ? permissionList.some(compare_func) : permissionList.every(compare_func)
  // };

  const isLogined = computed(() => !!token.value)

  const setToken = async (data: JwtToken) => {
    token.value = data
  }

  const login = async (data: UserLoginForm) => {
    const token_data = await userApi.login(data)
    await setToken(token_data)
    await nextTick()
    await freshUserInfo()
  }

  const logout = () => {
    token.value = undefined
    user.value = undefined
  }

  const freshUserInfo = async () => {
    try {
      user.value = await userApi.info()
    } catch {
      token.value = undefined
      user.value = undefined
    }
  }

  return {
    token,
    user,

    isLogined,

    login, logout, freshUserInfo, setToken,
    // compare_permission,
  }
}, {
  persist: {
    pick: ['token', 'user']
  }
});

export default useUserStore;
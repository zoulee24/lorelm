<route lang="yaml">
name: Login
path: /login
meta:
  title: 登录页
</route>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <el-form class="bg-white rounded-2xl shadow-xl p-8 space-y-2" :model="form" size="large" @submit.prevent="handleLogin">
        <div class="text-center">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">欢迎回来</h1>
          <p class="text-gray-600">请输入您的邮箱和密码登录</p>
        </div>

        <div class="space-y-4">
          <el-input
            v-model="form.username"
            type="email"
            placeholder="请输入邮箱地址"
            :class="{ 'border-red-500': errors.email }"
            autofocus autocomplete="email"
            @blur="validateEmail"
          >
            <template #prefix>
              <el-icon class="el-input__icon"><Icon icon="ic:baseline-email" /></el-icon>
            </template>
          </el-input>
          <div v-if="errors.username" class="text-red-500 text-sm">{{ errors.username }}</div>

          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
            autocomplete="current-password"
            :class="{ 'border-red-500': errors.password }"
            @blur="validatePassword"
          >
            <template #prefix>
              <el-icon class="el-input__icon"><Icon icon="ic:baseline-password" /></el-icon>
            </template>
          </el-input>
          <div v-if="errors.password" class="text-red-500 text-sm">{{ errors.password }}</div>
        </div>

        <div class="flex items-center justify-between">
          <el-checkbox v-model="form.remember">记住我</el-checkbox>
          <el-button type="text" class="text-blue-600">忘记密码？</el-button>
        </div>

        <el-button
          type="primary"
          size="large"
          native-type="submit"
          :loading="loading"
          class="w-full"
        >
          登录
        </el-button>

        <div class="text-center text-sm text-gray-600">
          还没有账号？
          <el-button type="text" class="text-blue-600" @click="$router.replace('/register')" :disabled="loading">立即注册</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>
<script setup lang="ts">
import type { UserLoginForm } from '@/schemas/admin'
import {Icon} from '@iconify/vue'
import useUserStore from '@/store/user'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()

interface LoginForm extends UserLoginForm {
  remember: boolean
}

const form = reactive<LoginForm>({
  username: '',
  password: '',
  remember: false
})

const errors = reactive<Record<keyof UserLoginForm, string>>({
  username: '',
  password: ''
})

const loading = ref(false)

const validateEmail = () => {
  if (!form.username) {
    errors.username = '请输入邮箱地址'
    return false
  }
  const emailRegex = /^([A-Za-z0-9_\-\.\u4e00-\u9fa5])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,8})$/
  if (!emailRegex.test(form.username)) {
    errors.username = '请输入有效的邮箱地址'
    return false
  }
  errors.username = ''
  return true
}

const validatePassword = () => {
  if (!form.password) {
    errors.password = '请输入密码'
    return false
  }
  if (form.password.length < 6) {
    errors.password = '密码长度不能少于6位'
    return false
  }
  // // 密码必须是数字和字母组合
  // const passwordRegex = /^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{6,}$/
  // if (!passwordRegex.test(form.password)) {
  //   errors.password = '密码必须是数字和字母组合'
  //   return false
  // }
  // 密码不能包含空格
  if (form.password.includes(' ')) {
    errors.password = '密码不能包含空格'
    return false
  }
  errors.password = ''
  return true
}

const validateForm = () => {
  const isEmailValid = validateEmail()
  const isPasswordValid = validatePassword()
  return isEmailValid && isPasswordValid
}

const handleLogin = async () => {
  if (!validateForm()) return

  loading.value = true
  try {
    // TODO: 调用登录API
    console.log('登录信息:', form)
    // await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟API调用

    await userStore.login(form)

    // 登录成功，检查是否有redirect参数
    const redirect = route.query.redirect as string
    const targetRoute = redirect || '/world'
    router.push(targetRoute)
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.warning('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>
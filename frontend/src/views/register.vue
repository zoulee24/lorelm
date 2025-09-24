<route lang="yaml">
name: Register
path: /register
meta:
  title: 注册页
</route>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <el-form class="bg-white rounded-2xl shadow-xl p-8 space-y-2" :model="form" size="large" @submit.prevent="handleRegister">
        <div class="text-center">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">创建账号</h1>
          <p class="text-gray-600">请填写以下信息完成注册</p>
        </div>

        <div class="space-y-1">
          <el-input
            v-model="form.email"
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
          <div v-if="errors.email" class="text-red-500 text-sm">{{ errors.email }}</div>

          <el-input
            v-model="form.nickname"
            placeholder="请输入用户名"
            :class="{ 'border-red-500': errors.nickname }"
            @blur="validateNickname"
          >
            <template #prefix>
              <el-icon class="el-input__icon"><Icon icon="mdi:account-circle-outline" /></el-icon>
            </template>
          </el-input>
          <div v-if="errors.nickname" class="text-red-500 text-sm">{{ errors.nickname }}</div>

          <el-input
            v-model="form.telephone"
            type="tel"
            placeholder="请输入手机号码（选填）"
            :class="{ 'border-red-500': errors.telephone }"
            @blur="validateTelephone"
            autocomplete="mobile tel-local"
          >
            <template #prefix>
              <el-icon class="el-input__icon"><Icon icon="mdi:phone-outline" /></el-icon>
            </template>
          </el-input>
          <div v-if="errors.telephone" class="text-red-500 text-sm">{{ errors.telephone }}</div>

          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
            autocomplete="new-password"
            :class="{ 'border-red-500': errors.password }"
            @blur="validatePassword"
          >
            <template #prefix>
              <el-icon class="el-input__icon"><Icon icon="ic:baseline-password" /></el-icon>
            </template>
          </el-input>
          <div v-if="errors.password" class="text-red-500 text-sm">{{ errors.password }}</div>

          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="请确认密码"
            show-password
            autocomplete="new-password"
            :class="{ 'border-red-500': errors.confirmPassword }"
            @blur="validateConfirmPassword"
          >
            <template #prefix>
              <el-icon class="el-input__icon"><Icon icon="ic:baseline-password" /></el-icon>
            </template>
          </el-input>
          <div v-if="errors.confirmPassword" class="text-red-500 text-sm">{{ errors.confirmPassword }}</div>

          <el-select
            v-model="form.gender"
            placeholder="请选择性别"
            class="w-full"
            :class="{ 'border-red-500': errors.gender }"
            @blur="validateGender"
          >
            <el-option label="男" value="男" />
            <el-option label="女" value="女" />
          </el-select>
          <div v-if="errors.gender" class="text-red-500 text-sm">{{ errors.gender }}</div>

          <el-select
            v-model="form.language"
            placeholder="请选择语言"
            class="w-full"
            :class="{ 'border-red-500': errors.language }"
            @blur="validateLanguage"
          >
            <el-option label="中文" value="zh-CN" />
            <el-option label="English" value="en-US" />
            <el-option label="日本語" value="ja-JP" />
          </el-select>
          <div v-if="errors.language" class="text-red-500 text-sm">{{ errors.language }}</div>

          <div class="flex items-center">
            <el-checkbox v-model="form.agree">
              我已阅读并同意
              <el-button type="text" class="text-blue-600" @click="showTerms">《用户协议》</el-button>
              和
              <el-button type="text" class="text-blue-600" @click="showPrivacy">《隐私政策》</el-button>
            </el-checkbox>
          </div>
          <div v-if="errors.agree" class="text-red-500 text-sm">{{ errors.agree }}</div>
        </div>

        <el-button
          type="primary"
          size="large"
          native-type="submit"
          :loading="loading"
          class="w-full"
        >
          注册
        </el-button>

        <div class="text-center text-sm text-gray-600">
          已有账号？
          <el-button type="text" class="text-blue-600" @click="$router.replace('/login')">立即登录</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import type { UserCreateForm } from '@/schemas/admin'

const router = useRouter()

interface CreateForm extends UserCreateForm{
  confirmPassword: string
  agree: boolean
}

const form = reactive<CreateForm>({
  email: '',
  nickname: '',
  password: '',
  confirmPassword: '',
  telephone: '',
  gender: '',
  language: 'zh-CN',
  agree: false
})

const errors = reactive<Record<keyof CreateForm, string>>({
  email: '',
  nickname: '',
  password: '',
  confirmPassword: '',
  telephone: '',
  gender: '',
  language: '',
  agree: ''
})

const loading = ref(false)

const validateEmail = () => {
  if (!form.email) {
    errors.email = '请输入邮箱地址'
    return false
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(form.email)) {
    errors.email = '请输入有效的邮箱地址'
    return false
  }
  errors.email = ''
  return true
}

const validateNickname = () => {
  if (!form.nickname) {
    errors.nickname = '请输入昵称'
    return false
  }
  if (form.nickname.length < 2) {
    errors.nickname = '昵称长度不能少于2位'
    return false
  }
  if (form.nickname.length > 20) {
    errors.nickname = '昵称长度不能超过20位'
    return false
  }
  errors.nickname = ''
  return true
}

const validateTelephone = () => {
  if (!form.telephone) {
    errors.telephone = ''
    return true
  }
  const phoneRegex = /^1[3-9]\d{9}$/
  if (!phoneRegex.test(form.telephone)) {
    errors.telephone = '请输入有效的手机号码'
    return false
  }
  errors.telephone = ''
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
  if (form.password.length > 20) {
    errors.password = '密码长度不能超过20位'
    return false
  }
  const passwordRegex = /^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{6,}$/
  if (!passwordRegex.test(form.password)) {
    errors.password = '密码必须是数字和字母组合'
    return false
  }
  if (form.password.includes(' ')) {
    errors.password = '密码不能包含空格'
    return false
  }
  errors.password = ''
  return true
}

const validateConfirmPassword = () => {
  if (!form.confirmPassword) {
    errors.confirmPassword = '请确认密码'
    return false
  }
  if (form.confirmPassword !== form.password) {
    errors.confirmPassword = '两次输入的密码不一致'
    return false
  }
  errors.confirmPassword = ''
  return true
}

const validateGender = () => {
  errors.gender = ''
  return true
}

const validateLanguage = () => {
  if (!form.language) {
    errors.language = '请选择语言'
    return false
  }
  errors.language = ''
  return true
}

const validateAgree = () => {
  if (!form.agree) {
    errors.agree = '请同意用户协议和隐私政策'
    return false
  }
  errors.agree = ''
  return true
}

const validateForm = () => {
  const isEmailValid = validateEmail()
  const isNicknameValid = validateNickname()
  const isTelephoneValid = validateTelephone()
  const isPasswordValid = validatePassword()
  const isConfirmPasswordValid = validateConfirmPassword()
  const isLanguageValid = validateLanguage()
  const isAgreeValid = validateAgree()

  return isEmailValid && isNicknameValid && isTelephoneValid &&
         isPasswordValid && isConfirmPasswordValid && isLanguageValid && isAgreeValid
}

const handleRegister = async () => {
  if (!validateForm()) return

  loading.value = true
  try {
    // TODO: 调用注册API
    console.log('注册信息:', {
      email: form.email,
      nickname: form.nickname,
      telephone: form.telephone,
      password: form.password,
      gender: form.gender,
      language: form.language
    })

    await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟API调用

    alert('注册成功！即将跳转到登录页')
    router.push('/login')
  } catch (error) {
    console.error('注册失败:', error)
    alert('注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const showTerms = () => {
  alert('用户协议内容')
}

const showPrivacy = () => {
  alert('隐私政策内容')
}
</script>
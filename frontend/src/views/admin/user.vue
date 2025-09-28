<route lang="yaml">
name: AdminUser
path: /admin/user
meta:
  title: 用户中心
</route>

<template>
  <div class="flex items-center justify-center h-screen">
    <el-card header="个人信息" class="max-w-150">
      <div class="flex items-center justify-between my-4">
        <el-text>修改</el-text>
        <el-switch v-model="change"></el-switch>
      </div>
      <el-form ref="formEl" :model="create_data" :disabled="!change" label-width="auto"
        @submit.prevent="handleSubmit">
        <el-row>
          <el-col :span="12">
            <el-form-item label="用户名" prop="nickname">
              <el-input v-model="create_data.nickname"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="create_data.email" autocomplete="email"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :hidden="!change" label="密码" prop="password">
              <el-input v-model="create_data.password" type="password" autocomplete="current-password"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :hidden="!change" label="确认">
              <el-input v-model="password" type="password" show-password></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机号码">
              <el-input v-model="create_data.telephone" type="telephone" autocomplete="tel-local"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="语言" prop="gender">
              <el-select v-model="create_data.language">
                <el-option label="简体中文" value="简体中文"></el-option>
                <el-option label="繁體中文" value="繁體中文"></el-option>
                <el-option label="English" value="English"></el-option>
                <el-option label="日本語" value="日本語"></el-option>
                <el-option label="한국어" value="한국어"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="create_data.gender">
                <el-radio label="男" value="男"></el-radio>
                <el-radio label="女" value="女"></el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <div class="flex items-center justify-center">
        <el-button v-if="!change" type="info" @click="logout" tabindex="5">登出</el-button>
        <el-button v-else type="info" @click="handleReset" tabindex="5">重置</el-button>
        <el-button v-show="change" type="primary" native-type="submit" tabindex="6" :disabled="!change">提交</el-button>
        <el-button v-show="!change" @click="$router.push('/')">主页</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import type { UserUpdateRequest } from '@/schemas/admin';
import useUserStore from '@/store/user';
import { storeToRefs } from 'pinia';
import { nextTick, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter()
const userStore = useUserStore()
const { user } = storeToRefs(userStore)
const change = ref(false)
const password = ref('')


const create_data = reactive<UserUpdateRequest>({
  nickname: '',
  email: '',
  gender: '男',
  telephone: '',
  password: '',
  language: '',
  disabled: false
})

const handleSubmit = () => {
}


const copyValue = () => {
  if (user.value) {
    Object.assign(create_data, user.value)
  }
}

const handleReset = copyValue


onMounted(() => {
  copyValue()
})

const logout = async () => {
  userStore.logout()
  await nextTick()
  router.push('/login')
}
</script>
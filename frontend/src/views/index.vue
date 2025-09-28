<route lang="yaml">
name: Index
path: /
meta:
  title: 根
</route>

<template>
  <div>
    <header class="header h-8">
      <el-segmented v-model="value" :options="options" :props="props" @change="onHeaderChange" />
      <div class="flex absolute right-0 top-0 h-full p-2">
        <el-dropdown>
          <el-avatar :src="userAvatar" class="rounded" fit="cover"></el-avatar>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="$router.push('/admin/user')">个人中心</el-dropdown-item>
              <el-dropdown-item @click="logout">登出</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>
    <main class="flex flex-col">
      <!-- <div class="flex flex-wrap"> -->
      <!-- <magic-card
          v-for="item in page.data"
          :key="item.id"
          :description="item.description || '神秘的魔法卡片'"
        >
          {{ item.nickname }}
        </magic-card> -->
      <!-- </div> -->
      <!-- <el-button>创建</el-button> -->
      <router-view></router-view>
    </main>
    <footer>
    </footer>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue';
import useUserStore from '@/store/user';
import { useRoute, useRouter } from 'vue-router';

const userStore = useUserStore()

const route = useRoute()
const router = useRouter()
const userAvatar = computed(() =>
  (userStore.user?.avatar ? '/file' + userStore.user.avatar : '/file/lorelm/resource/default_avatar.webp')
)

// const page = ref<PageResponse<CharacterResponse>>({
//   data: [],
//   total: 0
// })

const value = ref('/world')
const options = [
  {
    label: '世界',
    path: '/world'
  },
  {
    label: '角色',
    path: '/character'
  },
  {
    label: '对话',
    path: '/dialog'
  },
]
const props = {
  label: 'label',
  value: 'path',
  disabled: 'disabled',
}

const onHeaderChange = (v: string) => {
  router.push(v)
}

onMounted(() => {
  // characterApi.world.list().then(res => page.value = res)
  // characterApi.list().then(res => page.value = res)
  if (route.path === '/') {
    router.replace('/world')
  } else if (route.path.startsWith('/character')) {
    value.value = '/character'
  }
})

const logout = () => {
  userStore.logout()
  router.push('/login')
}
</script>


<style scoped> 
.header {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;

  padding: 8px 0;
  /* box */
  box-sizing: border-box;

  height: calc(var(--header-height) - 1px);
  
  border-bottom: 1px solid var(--el-border-color);
}

.header .el-segmented {
  --el-border-radius-base: 16px;
}
</style>

<style> 
.header .el-segmented .el-segmented__item {
  padding-left: 1rem;
  padding-right: 1rem;
}
</style>
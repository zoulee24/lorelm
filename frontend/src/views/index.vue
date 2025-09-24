<route lang="yaml">
name: Index
path: /
meta:
  title: 根
</route>

<template>
  <div>
    <header class="header">
      <el-segmented v-model="value" :options="options" />
    </header>
    <main>
      <div class="flex flex-wrap">
        <!-- <magic-card
          v-for="item in page.data"
          :key="item.id"
          :description="item.description || '神秘的魔法卡片'"
        >
          {{ item.nickname }}
        </magic-card> -->
        <magic-card
          v-for="item in page.data"
          :key="item.id"
          :description="item.description || '神秘的魔法卡片'"
        >
          {{ item.nickname }}
        </magic-card>
      </div>
    </main>
    <footer class="footer">
    </footer>
  </div>
</template>

<script lang="ts" setup>
import type { WorldResponse, CharacterResponse } from '@/schemas/character';
import characterApi from '@/api/character';
import type { PageResponse } from '@/schemas/base';
import { onMounted, ref } from 'vue';

// const page = ref<PageResponse<WorldResponse>>({
//   data: [],
//   total: 0
// })
const page = ref<PageResponse<CharacterResponse>>({
  data: [],
  total: 0
})

const value = ref('世界')
const options = ['世界', '角色']

onMounted(() => {
  // characterApi.world.list().then(res => page.value = res)
  characterApi.list().then(res => page.value = res)
})
</script>
<route lang="yaml">
name: Wrold
path: /world
meta:
  title: 世界
</route>

<template>
  <div class="flex flex-col gap-4 p-2">
    <div class="flex justify-center items-center flex-wrap gap-4">
      <magic-card
        class="w-full sm:w-[calc(50%-1rem)] lg:w-[calc(33.333%-1rem)] xl:w-[calc(18%-1rem)] h-64 sm:h-72 md:h-96 lg:h-118"
        v-for="item in page.data" :key="item.id" :description="item.description" :labels="item.labels"
        :title="item.nickname" @click="$router.push(`/world/${item.id}`)"></magic-card>
      <el-empty v-if="page.total === 0"></el-empty>
    </div>
    <el-button @click="visable.create = true">书写新的世界</el-button>
    <el-dialog v-model="visable.create" title="新的世界">
      <world-create @cancel="visable.create = false" @submit="onCreateSubmit"></world-create>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import type { WorldFullResponse } from '@/schemas/character';
import characterApi from '@/api/character';
import type { PageResponse } from '@/schemas/base';
import { onMounted, reactive, ref } from 'vue';
import WorldCreate from './components/WorldCreate.vue';


const page = ref<PageResponse<WorldFullResponse>>({
  data: [],
  total: 0
})

const visable = reactive({
  create: false,
})

onMounted(() => {
  characterApi.world.list().then(res => page.value = res)
})

const onCreateSubmit = (data: WorldFullResponse) => {
  page.value.total += 1
  page.value.data.unshift(data)
  visable.create = false
}
</script>
<route lang="yaml">
name: Character
path: /character
meta:
  title: 角色
</route>

<template>
  <div class="flex flex-col gap-4 p-2">
    <div class="flex justify-start items-center flex-wrap gap-4">
      <magic-card
        class="w-full sm:w-[calc(50%-1rem)] lg:w-[calc(33.333%-1rem)] xl:w-[calc(18%-1rem)] h-64 sm:h-72 md:h-96 lg:h-118"
        v-for="item in page.data" :key="item.id" :description="item.description" :avatar="showAvatar(item.avatar)"
        :labels="item.labels" :title="item.nickname" @click="$router.push(`/character/${item.id}`)" />
      <el-empty v-if="page.total === 0"></el-empty>
    </div>
    <el-button @click="visable.create = true">创造角色</el-button>
    <el-dialog v-model="visable.create" title="新的角色">
      <character-create @cancel="visable.create = false" @submit="onCreateSubmit"></character-create>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import type { CharacterResponse } from '@/schemas/character';
import characterApi from '@/api/character';
import type { PageResponse } from '@/schemas/base';
import { onMounted, reactive, ref } from 'vue';
import CharacterCreate from './components/CharacterCreate.vue';
import {showAvatar} from '@/utils';

const page = ref<PageResponse<CharacterResponse>>({
  data: [],
  total: 0
})

const visable = reactive({
  create: false,
})

onMounted(() => {
  characterApi.list().then(res => page.value = res)
})

const onCreateSubmit = (data: CharacterResponse) => {
  page.value.total += 1
  page.value.data.unshift(data)
  visable.create = false
}
</script>

<style scoped lang="scss"></style>
<route lang="yaml">
name: WroldDetail
meta:
  title: 世界细节
</route>
<template>
  <div class="flex flex-col gap-6 p-2">
    <header class="flex items-center justify-between">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/world' }">世界</el-breadcrumb-item>
        <el-breadcrumb-item>{{ world?.nickname || '未知世界' }}</el-breadcrumb-item>
      </el-breadcrumb>
    </header>

    <main v-if="loading" class="flex items-center justify-center h-64">
      <el-skeleton :rows="3" animated />
    </main>

    <main v-else-if="error" class="flex items-center justify-center h-64">
      <el-empty description="加载失败" />
    </main>

    <main v-else>
      <!-- 世界基础信息 -->
      <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div class="mb-4">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ world?.nickname || '未知世界' }}</h1>
          <markdown-render :content=" world?.description"></markdown-render>
        </div>

        <!-- 标签展示 -->
        <div v-if="world?.labels && world.labels.length > 0" class="flex flex-wrap gap-2 mb-2">
          <el-tag
            v-for="label in world.labels"
            :key="label"
            type="info"
          >
            {{ label }}
          </el-tag>
        </div>
      </div>

      <!-- 关联角色 -->
      <div v-if="relate_characters.length > 0">
        <h2 class="text-2xl font-semibold text-gray-900 mb-4">关联角色</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <magic-card
            v-for="character in relate_characters"
            :key="character.id"
            :title="character.nickname"
            :description="character.description"
            :firstMessage="character.first_message"
            :labels="character.labels"
            @click="navigateToCharacter(character.id)"
          />
        </div>
      </div>

      <div v-else>
        <el-empty description="暂无关联角色" />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';

import MarkdownRender from '@/components/MarkdownRender';
import type { WorldFullResponse, CharacterResponse } from '@/schemas/character';
import characterApi from '@/api/character';

const route = useRoute("WroldDetail")
const router = useRouter()
const world_id = parseInt(route.params.id)

// 加载状态
const loading = ref(true)
// 错误状态
const error = ref(false)

// 世界信息
const world = ref<WorldFullResponse>()
// 世界关联的角色
const relate_characters = ref<CharacterResponse[]>([])

// 跳转到角色详情页
const navigateToCharacter = (characterId: number) => {
  router.push(`/character/${characterId}`)
}

onMounted(async () => {
  try {
    loading.value = true
    error.value = false

    // 获取世界信息
    const worldData = await characterApi.world.info(world_id)
    world.value = worldData

    // 获取关联角色
    const charactersData = await characterApi.world.characters(world_id)
    relate_characters.value = charactersData

  } catch (err) {
    console.error('加载世界信息失败:', err)
    error.value = true
    ElMessage.error('加载世界信息失败')
  } finally {
    loading.value = false
  }
})


</script>
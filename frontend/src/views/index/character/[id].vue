<route lang="yaml">
name: CharacterDetail
meta:
  title: 角色信息
</route>
<template>
  <div class="flex flex-col gap-6 p-2">
    <header class="flex items-center justify-between">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/character' }">角色</el-breadcrumb-item>
        <el-breadcrumb-item>{{ character?.nickname || '新角色' }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div class="right flex">
        <el-button type="danger" @click="handleDelete" circle>
          <template #icon>
            <el-icon size="18">
              <Icon icon="material-symbols:delete-outline" />
            </el-icon>
          </template>
        </el-button>
        <el-button circle>
          <template #icon>
            <el-icon size="16">
              <Icon icon="material-symbols:edit-outline" />
            </el-icon>
          </template>
        </el-button>
      </div>
    </header>

    <main v-if="loading" class="flex items-center justify-center h-64">
      <el-skeleton :rows="3" animated />
    </main>

    <main v-else-if="error" class="flex items-center justify-center h-64">
      <el-empty description="加载失败" />
    </main>

    <main v-else>
      <!-- 角色展示 -->
      <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div class="flex items-start gap-6 mb-6">
          <div class="flex-shrink-0">
            <el-image :src="characterAvatar" class="w-32 h-32 rounded-full object-cover" fit="cover" />
          </div>
          <div class="flex-1">
            <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ character!.nickname }}</h1>
            <markdown-render class="text-gray-600 mb-4" :content="character!.description"></markdown-render>

            <!-- 标签 -->
            <div v-if="character?.labels && character.labels.length > 0" class="flex flex-wrap gap-2 mb-4">
              <el-tag v-for="label in character.labels" :key="label" type="info">
                {{ label }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 首条信息 -->
        <div class="border-t pt-4">
          <h3 class="text-lg font-semibold text-gray-900 mb-3">首条消息</h3>
          <div class="bg-gray-50 rounded-lg p-4">
            <markdown-render :content="character?.first_message" />
          </div>
        </div>
      </div>

      <!-- 关联世界 -->
      <div v-if="related_world">
        <h2 class="text-2xl font-semibold text-gray-900 mb-4">@^L</h2>
        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center gap-4 cursor-pointer hover:bg-gray-50 rounded-lg p-4 transition-colors"
            @click="navigateToWorld(related_world.id)">
            <div class="flex-shrink-0">
              <div
                class="w-16 h-16 bg-gradient-to-br from-blue-400 to-blue-600 rounded-lg flex items-center justify-center text-white text-xl font-bold">
                {{ related_world.nickname?.charAt(0) || '' }}
              </div>
            </div>
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-gray-900">{{ related_world.nickname }}</h3>
              <p class="text-gray-600 text-sm mt-1">{{ related_world.description?.substring(0, 100) || '����' }}...</p>
            </div>
            <el-icon>
              <Icon icon="" />
            </el-icon>
          </div>
        </div>
      </div>
      <div v-else>
        <el-empty description="暂无关联世界" />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { Icon } from '@iconify/vue';
import { computed, onMounted, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import MarkdownRender from '@/components/MarkdownRender';
import type { CharacterResponse, WorldFullResponse } from '@/schemas/character';
import characterApi from '@/api/character';
import { ElMessage, ElMessageBox } from 'element-plus';

const route = useRoute("CharacterDetail")
const router = useRouter()
const character_id = parseInt(route.params.id)

const loading = ref(true)
const error = ref(false)

const character = ref<CharacterResponse>()
const related_world = ref<WorldFullResponse>()

const characterAvatar = computed(() => {
  if (character.value?.avatar) {
    return `/file${character.value.avatar}`;
  }
  return '/file/lorelm/resource/default_avatar.webp';
})


const navigateToWorld = (worldId: number) => {
  router.push(`/world/${worldId}`)
}

const handleDelete = async () => {
  try {
    // 二次确认弹窗
    await ElMessageBox.confirm(
      `确定要删除角色 [${character.value?.nickname}] 吗？此操作不可撤销。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    // 调用删除API
    await characterApi.del(character_id)

    // 跳转到角色列表页面
    router.back()
  } catch (error) {
    if (error === 'cancel') {
      // 用户取消删除操作
      return
    }
    // 其他错误
    console.error('删除角色失败:', error)
    ElMessage.error('删除角色失败')
  }
}

onMounted(async () => {
  try {
    loading.value = true
    error.value = false

    // 获取角色信息
    const characterData = await characterApi.info(character_id)
    character.value = characterData

    // 获取关联世界
    if (characterData.world_id) {
      const worldData = await characterApi.world.info(characterData.world_id)
      related_world.value = worldData
    }

  } catch (err) {
    console.error(err)
    error.value = true
  } finally {
    loading.value = false
  }
})
</script>
<template>
  <el-form class="flex flex-col gap-4" @submit.prevent="onClickCreate">
    <div class="flex gap-4" :class="{ 'flex-col': !select_world }">
      <el-tag>世界</el-tag>
      <div class="show-card hide-scrollbar" v-if="!select_world">
        <magic-card class="h-64 w-64" v-for="item in world_page.data" :key="item.id" :title="item.nickname"
          :description="item.description" @click="select_world = item" />
      </div>
      <div class="flex gap-4" v-else>
        <magic-card class="h-32 w-32" :title="select_world.nickname" :description="select_world.description" active
          @click="select_world = undefined" />
      </div>
    </div>
    <div class="flex flex-col gap-4" v-show="select_world && world_relate_characters.length > 0">
      <el-tag>{{ select_world?.nickname + '角色' }}</el-tag>
      <div class="show-card hide-scrollbar">
        <magic-card class="h-64 w-64" v-for="item in world_relate_characters" :key="item.id" :title="item.nickname"
          :description="item.description" />
      </div>
    </div>
    <div class="flex flex-col gap-4">
      <el-tag>角色</el-tag>
      <div class="show-card hide-scrollbar">
        <template v-for="item in character_page.data" :key="item.id">
          <magic-card class="h-64 w-64" :title="item.nickname"
            v-if="!select_characters.map(it => it.id).includes(item.id)" :description="item.description"
            @click="select_characters.unshift(item)" />
        </template>
      </div>
      <el-tag>选择角色</el-tag>
      <div class="show-card hide-scrollbar">
        <template v-for="item in select_characters" :key="item.id">
          <magic-card class="h-32 w-32" :title="item.nickname" :description="item.description" active
            @click="select_characters.splice(select_characters.indexOf(item), 1)" />
        </template>
      </div>
    </div>
    <div class="flex">
      <el-button>取消</el-button>
      <el-button type="success" native-type="submit">开始</el-button>
    </div>
  </el-form>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue';

import characterApi from '@/api/character';
import type { PageResponse } from '@/schemas/base';
import type { CharacterResponse, WorldResponse } from '@/schemas/character';
import { ElMessage } from 'element-plus';

export interface CreateForm {
  characters: CharacterResponse[]
  world?: WorldResponse
  act_character?: CharacterResponse
}

interface Emits {
  (e: 'submit', form: CreateForm): void
}
const emit = defineEmits<Emits>()


const world_page = ref<PageResponse<WorldResponse>>({
  data: [],
  total: 0
})
const world_relate_characters = ref<CharacterResponse[]>([])
const character_page = ref<PageResponse<CharacterResponse>>({
  data: [],
  total: 0
})

const select_world = ref<WorldResponse>()
const select_characters = ref<CharacterResponse[]>([])
const select_act_character_id = ref<CharacterResponse>()

onMounted(() => {
  characterApi.world.list().then(res => world_page.value = res)
  characterApi.list().then(res => character_page.value = res)
})

const onClickCreate = () => {
  if (select_characters.value.length === 0) {
    ElMessage.info('请选择角色')
    return;
  }
  emit('submit', {
    characters: select_characters.value,
    world: select_world.value,
    act_character: select_act_character_id.value,
  })
}

</script>

<style scoped lang="scss">
.show-card {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  justify-content: center;

  gap: 1rem;

  overflow-y: auto;

  max-height: 300px;
}
</style>
<template>
  <div class="__card" @mouseenter="hover = true" @mouseleave="hover = false">
    <el-image v-if="avatar" class="image" :src="avatar" alt="角色图片" fit="cover" lazy></el-image>
    <div class="detail">
      <el-tag size="large" v-show="!(hover && active)">{{ title }}</el-tag>
      <div v-if="labels && labels.length > 1 && !active" class="flex flex-warp gap-2">
        <el-tag size="small" v-for="label in labels" type="info">{{ label }}</el-tag>
      </div>
      <div v-show="hover && !active" class="description hide-scrollbar">
        {{ description }}
      </div>
      <el-button v-show="hover && active" type="danger" link size="large">
        <template #icon>
          <el-icon size="26">
            <Icon icon="material-symbols:delete-outline" />
          </el-icon>
        </template>
      </el-button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed, ref, watch } from 'vue'
import { Icon } from '@iconify/vue'

interface Props {
  avatar?: string
  title: string
  description: string
  active?: boolean
  labels?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  avatar: '',
  description: '',
  active: false,
  labels: () => []
})

const hover = ref(false)

</script>

<style scoped lang="scss">
.__card {
  position: relative;

  user-select: none;

  display: flex;
  background-color: aliceblue;

  border-radius: 1rem;

  gap: .5rem;

  .image {
    position: absolute;

    height: 100%;
    width: 100%;

    border-radius: 1rem;
    top: 0;
    left: 0;

    z-index: 0;
  }

  .detail {
    display: flex;
    flex-direction: column;

    padding: 1rem;

    justify-content: center;
    align-items: center;

    gap: .5rem;

    width: 100%;
    height: 100%;
    border-radius: 1rem;
    transition: background-color .3s;

    z-index: 1;

    .description {
      width: 100%;
      height: 100%;
      overflow-y: scroll;
    }
  }

  .detail:hover {
    cursor: pointer;
    background-color: rgba(0, 0, 0, 0.6);
    color: whitesmoke;
  }
}
</style>
<template>
  <div class="__card" @mouseenter="hover = true" @mouseleave="hover = false">
    <el-image v-if="avatar" class="image" :src="avatar" alt="角色图片" fit="cover" lazy></el-image>
    <div class="detail">
      <el-tag size="large" v-show="!(hover && active)">{{ title }}</el-tag>
      <div v-show="hover && !active" class="description hide-scrollbar">
        {{ description }}
      </div>
      <el-button v-show="hover && active" type="danger" link size="large">
        <template #icon>
          <el-icon size="26">
            <Icon icon="material-symbols:delete-outline"/>
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
}

const props = withDefaults(defineProps<Props>(), {
  avatar: 'https://image.huanghepiao.com/d/file/20200801/761c78baca90bfd1cbfc94d266f71240.png',
  description: '',
  active: false
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
    transition: all .3s;

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
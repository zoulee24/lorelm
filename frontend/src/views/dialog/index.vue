<route lang="yaml">
name: Dialog
path: /dialog
meta:
  title: 对话页
</route>

<template>
  <div class="h-screen flex items-center justify-center relative">
    <div class="absolute top-2 left-2">
      <el-button circle @click="visable.sidebar = true">
        <template #icon>
          <el-icon size="18">
            <Icon icon="tabler:layout-sidebar-left-expand" />
          </el-icon>
        </template>
      </el-button>
      <transition name="slide">
        <side-bar v-show="visable.sidebar" :datas="[]" :class="{ 'slide-out': !visable.sidebar }"
          @on-hide="visable.sidebar = false" @on-select="" />
      </transition>
    </div>
    <main class="dialog gap-2">
      <chat-history class="messages"></chat-history>
      <chat-input></chat-input>
    </main>
  </div>
</template>

<script lang="ts" setup>
import { Icon } from '@iconify/vue'
import { onMounted, reactive, ref } from 'vue';
import sideBar from './components/sideBar.vue'
import type { ConversationSession } from '@/schemas/conversation';

const visable = reactive({
  sidebar: false
})
const sessions = ref<ConversationSession[]>([])
const session = ref<ConversationSession>()

onMounted(() => {
  
})

</script>

<style lang="scss" scoped>
.dialog {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;

  width: 100%;
  height: 100%;
  padding: 1rem;
  max-width: 46rem;
}

.dialog>.messages {
  height: 100%;
  overflow-y: scroll;
  scrollbar-width: none;

  &::-webkit-scrollbar {
    display: none;
  }
}

.side-bar {
  position: absolute;
  top: 0;
  left: 0;

  width: 100%;
  max-width: min(16rem, 100%);
  height: 100%;

  z-index: 1;
}

/* 侧边栏滑入滑出动画 */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.5s ease-out;
}

.slide-enter-from {
  transform: translateX(-100%);
  opacity: 0;
}

.slide-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}

/* 确保过渡组件内部元素的宽度正确 */
.slide-enter-active,
.slide-leave-active {
  width: 100%;
  max-width: min(16rem, 100%);
}

/* 确保侧边栏组件的宽度 */
.side-bar :deep(> div) {
  width: 100%;
  max-width: min(16rem, 100%);
}
</style>
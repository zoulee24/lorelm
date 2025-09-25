<template>
  <div class="bar">
    <div class="flex items-center justify-between mb-4">
      <el-text>{{ title ?? 'LoreLM' }}</el-text>
      <el-button circle @click="$emit('hide')">
        <template #icon>
          <el-icon size="18">
            <Icon icon="tabler:layout-sidebar-left-collapse" />
          </el-icon>
        </template>
      </el-button>
    </div>
    <el-button class="item" @click="createSession">{{ createText ?? '开始新的旅程' }}</el-button>
    <div class="list mt-2">
      <button v-for="item in datas" class="item p-2 rounded-xl" :key="item.id"
        :class="{ 'selected': activeId === item.id }" @click="selectItem(item)">
        <el-text truncated line-clamp="1">{{ item.content }}</el-text>
      </button>
    </div>
  </div>
</template>
<script setup lang="ts">
import { Icon } from '@iconify/vue';
import { ref } from 'vue';

interface Props {
  title?: string,
  datas?: { id: number, content: string }[],
  createText?: string
}
const props = defineProps<Props>()
interface Emits {
  (e: "select", id: number): void
  (e: "hide"): void
  (e: "create"): void
}
const emits = defineEmits<Emits>()

const activeId = ref<number>()

const createSession = () => {
  emits('hide')
  emits('create')
}
const selectItem = (item: { id: number, content: string }) => {
  console.log(item)
  activeId.value = item.id
  emits('select', item.id)
}
</script>
<style lang="scss" scoped>
.bar {
  display: flex;
  flex-direction: column;
  justify-content: start;

  padding: 1rem;
  height: 100%;
  width: 100%;
  max-width: min(16rem, 100%);

  background-color: whitesmoke;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 100;
  transition: all 0.5s ease-out;

  &.slide-out {
    transform: translateX(-100%);
    opacity: 0;
  }
}

@keyframes slideInLeft {
  from {
    transform: translateX(-100%);
    opacity: 0;
  }

  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.list {
  display: flex;
  flex-direction: column;
  justify-content: start;
  align-items: center;
  flex-grow: 1;
  overflow-y: auto;

  .item {
    text-align: start;
  }

  .item:active,
  .item:hover,
  .selected {
    background-color: rgba(199, 199, 199, 0.5);
  }

  /* 隐藏滚动条但保持滚动功能 */
  &::-webkit-scrollbar {
    display: none;
  }

  /* Firefox */
  scrollbar-width: none;
}

.bar .item {
  width: 100%;
}
</style>
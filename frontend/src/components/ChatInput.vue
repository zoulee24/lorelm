<template>
  <div class="user-input gap-2">
    <el-collapse-transition>
      <div v-show="showCreate" class="outer">
        <el-button plain round @click="$emit('create')">
          {{ createText }}
          <template #icon>
            <el-icon>
              <Icon icon="lsicon:add-chat-outline" />
            </el-icon>
          </template>
        </el-button>
      </div>
    </el-collapse-transition>
    <el-text class="w-full h-full">
      <textarea v-model="modelValue" type="text" autofocus rows="2" placeholder="尽管问..." inputmode="text"
        @keydown.enter.exact.prevent="handleEnter" :disabled="loading"></textarea>
    </el-text>
    <div class="flex items-center justify-between w-full">
      <div>
        <el-button circle :disabled="loading">
          <template #icon>
            <el-icon>
              <Icon icon="mdi:tools" />
            </el-icon>
          </template>
        </el-button>
        <el-button round :type="utils.deepresearch ? 'primary' : 'default'"
          @click="utils.deepresearch = !utils.deepresearch" :disabled="loading">
          <template #icon>
            <el-icon size="20">
              <Icon icon="tabler:microscope" />
            </el-icon>
          </template>
          深度研究
        </el-button>
        <el-button round :type="utils.thinking ? 'primary' : 'default'" @click="utils.thinking = !utils.thinking"
          :disabled="loading">
          <template #icon>
            <el-icon size="20">
              <Icon icon="meteor-icons:meta" />
            </el-icon>
          </template>
          思考
        </el-button>
      </div>
      <div>
        <el-button circle :disabled="loading">
          <template #icon>
            <el-icon size="20">
              <Icon icon="ion:attach" />
            </el-icon>
          </template>
        </el-button>
        <el-button circle type="info" :disabled="modelValue.length === 0" :loading="loading" @click="handleSubmit">
          <template #icon>
            <el-icon size="16">
              <Icon icon="icon-park-outline:arrow-up" />
            </el-icon>
          </template>
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Icon } from '@iconify/vue';
import { reactive } from 'vue';

interface Utils {
  deepresearch: boolean
  thinking: boolean
  files: File[]
}
export interface ChatInfo {
  content: string
  utils: Utils
}

interface Props {
  loading?: boolean
  showCreate?: boolean
  createText?: string
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  showCreate: true,
  createText: '开启新的探险'
})

// 定义组件事件类型
interface UserInputEmits {
  (e: 'create'): void
  (e: 'submit', value: ChatInfo, callback: () => void): void
}

const utils = reactive<Utils>({
  deepresearch: false,
  thinking: false,
  files: [],
})
const modelValue = defineModel<string>({ required: false, default: '' })

// 定义组件事件
const emit = defineEmits<UserInputEmits>()

// 处理回车键
const handleEnter = (event: KeyboardEvent) => {
  if (event.key !== 'Enter') return;
  if (event.ctrlKey || event.shiftKey) modelValue.value += '\n'
  else handleSubmit()
}
// 提交表单
const handleSubmit = () => {
  if (modelValue.value.trim().length > 0) {
    emit('submit', {
      content: modelValue.value,
      utils: utils
    } as ChatInfo, clearText)
  }
}

const clearText = () => {
  modelValue.value = ''
  utils.files.length = 0
}

// 导出方法供父组件调用
defineExpose({ clearText })
</script>

<style lang="scss" scoped>
.user-input .outer {
  display: inline-flex;
  align-items: center;
  justify-content: space-between;

  position: absolute;
  left: 0;
  top: -40px;
}

.user-input {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-width: 1px;
  border-style: solid;
  border-radius: 1rem;
  width: 100%;
  padding: 0.5rem;
  border-color: rgb(209, 216, 216);

  position: relative;

  textarea {
    background: transparent;
    border: none;
    outline: none;
    width: 100%;
    min-height: 24px;
    max-height: 48px;
    resize: none;
    color: inherit;
    font-family: inherit;
    font-size: inherit;

    &::placeholder {
      color: #999;
    }
  }

  .el-button {
    transition: all 0.2s ease;
  }
  // 不要太生硬
  transition: all 0.5s ease;
}

.user-input:hover {
  box-shadow: 0 0 18px rgba(0, 0, 0, 0.1);
}
</style>
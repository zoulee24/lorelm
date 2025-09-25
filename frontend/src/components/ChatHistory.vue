<template>
  <div ref="message" class="dialog-container">
    <template v-for="message in showMessages">
      <div class="message" :class="message.role == 'user' ? 'user' : 'assistant'" v-if="message.content.length != 0">
         <markdown-render :content="message.content"></markdown-render>
      </div>
    </template>
  </div>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue';

import type { ChatMessage } from '@/schemas/conversation';

const message = ref<HTMLDivElement>();

interface Props {
  messages?: ChatMessage[]
}
const props = withDefaults(defineProps<Props>(), {
  messages: () => ([])
});
// const props = withDefaults(defineProps<Props>(), {
//   messages: () => ([{ role: 'user', content: '就放到生警方弄的时间' }, { role: 'assistant', content: '*$就放到生警方弄的时间$*', reasoning: '就放到生警方弄的时间' }])
// });

interface Expose {
  scrollToBottom: (behavior?: ScrollBehavior) => void
}

const scrollToBottom = (behavior?: ScrollBehavior) => message.value?.scrollTo({
    top: message.value.scrollHeight,
    behavior
  })

defineExpose<Expose>({
  scrollToBottom
})

const showMessages = computed(() => {
  return props.messages.filter(message => message.role === 'user' || message.role === 'assistant').map(message => ({
    role: message.role,
    content: showContent(message),
    finished: message.finished,
  }))
})
const showContent = (data: ChatMessage) => {
  if (data.role === 'user') return data.content.trim();
  let content = data.content.trim().replace(/##\s*\d+\s*~~/g, '').replace(/#*$/, '');
  if (data.reasoning) {
    const reasoning = data.reasoning.trim().replace(/##\s*\d+\s*~~/g, '').replace(/#*$/, '');
    // 适用正则去除 ##\s*\d+\s*$$
    return `<think>\n${reasoning}\n</think>\n\n${content}`
  } else return content;
}
</script>

<style lang="scss" scoped>
.dialog-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;

  .message {
    padding: 12px 16px;
    margin-bottom: 16px;
    border-radius: 18px;
    max-width: 90%;
    line-height: 1.5;
    background-color: var(--el-bg-color-page);
  }

  .user {
    align-self: flex-end;
    border-bottom-right-radius: 4px;
  }

  .assistant {
    align-self: flex-start;
    border-bottom-left-radius: 4px;
  }
}
</style>
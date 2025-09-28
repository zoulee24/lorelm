<route lang="yaml">
name: Dialog
path: /dialog
meta:
  title: 对话页
</route>

<template>
  <div class="viewer">
    <div class="absolute top-2 left-2">
      <div class="inline-flex">
        <el-button circle @click="visable.sidebar = true">
          <template #icon>
            <el-icon size="18">
              <Icon icon="tabler:layout-sidebar-left-expand" />
            </el-icon>
          </template>
        </el-button>
        <el-button circle @click="visable.create = true">
          <template #icon>
            <el-icon size="18">
              <Icon icon="lsicon:add-chat-outline" />
            </el-icon>
          </template>
        </el-button>
      </div>
      <transition name="slide">
        <side-bar v-show="visable.sidebar" :datas="showSidBar" :class="{ 'slide-out': !visable.sidebar }"
          @hide="visable.sidebar = false" @select="onSelect" @create="visable.create = true" />
      </transition>
    </div>
    <main class="dialog gap-2">
      <chat-history  ref="history" class="messages hide-scrollbar" :messages="showMessages"></chat-history>
      <chat-input :loading="loading.input" @submit="onCreateDialog" @create="visable.create = true" :show-create="showMessages.length === 0"></chat-input>
    </main>
    <el-dialog v-model="visable.create" title="新的旅程">
      <create-session @cancel="visable.create = false" @submit="onSubmit"></create-session>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { Icon } from '@iconify/vue'
import { computed, nextTick, onMounted, reactive, ref } from 'vue';
import type {ChatInfo} from '@/components/ChatInput.vue'
import SideBar from './components/sideBar.vue'
import CreateSession from './components/createSession.vue'
import type { CreateForm } from './components/createSession.vue'
import ChatHistory from '@/components/ChatHistory.vue';
import type { SessionResponse, SessionMessageResponse, ConversationCreateForm, ConversationHistory } from '@/schemas/conversation';
import { sessionApi } from '@/api/conversation'
import { ElMessage } from 'element-plus';


const loading = reactive({
  input: false,
  create: false,
})

const visable = reactive({
  sidebar: false,
  create: false,
})
const sessions = ref<SessionResponse[]>([])
const session = ref<SessionMessageResponse>()

const history = ref<InstanceType<typeof ChatHistory>>()

const showSidBar = computed(() => (sessions.value.map(it => ({
  id: it.id,
  content: it.title
}))))
const showMessages = computed(() => {
  if (!session.value?.messages) return [];
  return session.value.messages;
})

const on_select_session = (session_id: number) => 
  sessionApi.info(session_id).then(res => {
    session.value = res
    return nextTick(() => history.value?.scrollToBottom('instant'))
  })

onMounted(() => {
  sessionApi.list().then(res => {
    sessions.value = res
    if (res.length > 0 && res[0]) {
      on_select_session(res[0].id)
    }
  })
})

const onCreateDialog =  (data: ChatInfo, clearText: () => void) => {
  if (!session.value) return;
  loading.input = true

  streaming(data.content, session.value.id, clearText).finally(() => {
    loading.input = false
  })
}

const streaming = async (query: string, session_id: number, clearText: () => void) => {
  const rsp = await sessionApi.chat(query, session_id);
  for await (const chunk of rsp) {
    if (chunk.type == 'output') {
      if (chunk.data.content) {
        session.value!.messages[session.value!.messages.length - 1]!.content += chunk.data.content;
      } else if (chunk.data.reasoning) {
        session.value!.messages[session.value!.messages.length - 1]!.reasoning += chunk.data.reasoning;
      }
      history.value?.scrollToBottom('smooth')
    } else if (chunk.type == 'reference') {
      const docs = chunk.data.docs ?? [];
      ElMessage.success({
        message: `检索到 ${docs.length} 条参考信息`,
        duration: 3000,
      })
    } else if (chunk.type == 'rewrite') {
      ElMessage.info({
        message: "您可能想问：" + chunk.data.content,
        duration: 3000,
      })
    } else if (chunk.type === 'session_created') {
      const ss = chunk.data as SessionMessageResponse;
      ss.messages = []
      session.value = ss;
      sessions.value.unshift(session.value);
      // console.log('session_created', ss, session.value);
    } else if (chunk.type === 'dialog_created') {
      const ss = chunk.data as ConversationHistory;
      session.value!.messages.push(ss);
      history.value!.scrollToBottom('smooth')
      if (!session.value!.title) {
        session.value!.title = ss.content.substring(0, 32);
      }
      // 创建会话后清除输入框输入
      if (ss.role === 'user') clearText()
    } else if (chunk.type === 'done') {
      history.value?.scrollToBottom('smooth')
    } else if (chunk.type === 'notice') {
      ElMessage.info({
        message: chunk.data.content,
        duration: 3000,
      })
    } else if (chunk.type === 'tts') {
      const base64_mp3_data = chunk.data.data
      playBase64Audio(base64_mp3_data)
    } else {
      console.log("未知事件类型: ", chunk.type);
    }
  }
}

// 播放base64编码的MP3音频
const playBase64Audio = (base64Data: string) => {
  // 将base64数据转换为Blob
  const binaryString = atob(base64Data);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  
  const blob = new Blob([bytes], { type: 'audio/mp3' });
  const audioUrl = URL.createObjectURL(blob);
  
  // 创建audio元素并播放
  const audio = new Audio(audioUrl);
  audio.play()
    .then(() => {
      console.log('音频播放成功');
      // 播放完毕后释放资源
      audio.addEventListener('ended', () => {
        URL.revokeObjectURL(audioUrl);
      });
    })
    .catch(error => {
      console.error('音频播放失败:', error);
      URL.revokeObjectURL(audioUrl);
    });
}

const onSubmit = (data: CreateForm) => {
  const form = {
    character_ids: data.characters.map(item => item.id),
    world_id: data.world?.id,
    act_character_id: data.act_character?.id,
  } as ConversationCreateForm;

  loading.create = true
  sessionApi.create(form).then(res => {
    session.value = res;
    sessions.value.unshift(res);
    visable.create = false;
  }).finally(() => {
    loading.create = false
  })

}

const onSelect = (session_id: number) => {
  const s = sessions.value.find(it => (it.id == session_id))
  if (!s) {
    ElMessage.warning('会话不存在')
    return;
  }
  loading.input = true
  sessionApi.info(session_id).then(res => {
    session.value = res
  }).catch(console.warn).finally(() => {
    loading.input = false
  })
  setTimeout(() => {
    visable.create = false
  }, 100)
}

</script>

<style lang="scss" scoped>
.viewer {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: calc(100vh - var(--header-height));
}

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

.create-session {
  padding: 1rem;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.1);
}
</style>
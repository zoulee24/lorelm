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
        <side-bar v-show="visable.sidebar" :datas="showSidBar" :class="{ 'slide-out': !visable.sidebar }"
          @hide="visable.sidebar = false" @select="onSelect" @create="visable.create = true" />
      </transition>
    </div>
    <main class="dialog gap-2">
      <chat-history ref="history" class="messages hide-scrollbar" :messages="showMessages"></chat-history>
      <chat-input :loading="loading.input" @submit="onCreateDialog"></chat-input>
    </main>
    <el-dialog v-model="visable.create" title="新的旅程">
      <create-session @submit="onSubmit"></create-session>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { Icon } from '@iconify/vue'
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue';
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
})

const visable = reactive({
  sidebar: false,
  create: false,
})
const sessions = ref<SessionResponse[]>([])
const session = ref<SessionMessageResponse>()
const new_dialog_form = ref<ConversationCreateForm>()

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
  let form: ConversationCreateForm | string
  if (!session.value) {
    if (!new_dialog_form.value) return;
    new_dialog_form.value.content = data.content
    form = new_dialog_form.value
  } else {
    form = data.content
  }

  loading.input = true

  streaming(form, session.value?.id).then(() => {
    clearText()
  }).finally(() => {
    loading.input = false
  })
}

const streaming = async (form: ConversationCreateForm | string, session_id?: number) => {
  const rsp = await sessionApi.create(form, session_id);
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
      // info.history[info.history.length - 1].refs!.push(...chunk.data.docs);
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
      console.log('session_created', ss, session.value);
    } else if (chunk.type === 'dialog_created') {
      const ss = chunk.data as ConversationHistory;
      session.value!.messages.push(ss);
      history.value?.scrollToBottom('smooth')
    } else if (chunk.type === 'done') {
      history.value?.scrollToBottom('smooth')
    } else {
      console.log("未知事件类型: ", chunk.type);
    }
  }
}

const onSubmit = (data: CreateForm) => {
  console.log(data);
  new_dialog_form.value = {
    character_ids: data.characters.map(item => item.id),
    world_id: data.world?.id,
    act_character_id: data.act_character?.id,
    content: '',
  };
  visable.create = false;
  session.value = undefined;
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
</style>
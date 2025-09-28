<template>
  <el-form @submit.prevent="onSubmit">
    <div class="flex items-center justify-between gap-2">
      <el-form-item>
        <el-upload class="avatar-uploader" accept=".png,.jpg,.jpeg,.webp" :show-file-list="false" :auto-upload="false"
          :on-change="handleAvatarChange">
          <el-avatar :size="48" fit="cover" :src="showAvatarPerview">
          </el-avatar>
        </el-upload>
      </el-form-item>
      <el-form-item class="w-full" prop="nickname" label="名称">
        <el-input v-model="create_data.nickname" maxlength="16"></el-input>
      </el-form-item>
    </div>
    <el-form-item prop="description" label="描述">
      <el-input type="textarea" v-model="create_data.description" :autosize="{ minRows: 3, maxRows: 6 }" resize="none"
        show-word-limit></el-input>
    </el-form-item>
    <el-form-item prop="first_message" label="首条消息">
      <el-input type="textarea" v-model="create_data.first_message" :autosize="{ minRows: 3, maxRows: 6 }" resize="none"
        show-word-limit></el-input>
    </el-form-item>
    <el-form-item prop="data_range" label="可见访问">
      <el-select v-model="create_data.data_range">
        <el-option label="公开" value="all"></el-option>
        <el-option label="私有" value="self"></el-option>
      </el-select>
    </el-form-item>
    <el-form-item prop="labels" label="标签">
      <el-select v-model="create_data.labels" multiple allow-create remote filterable reserve-keyword clearable
        collapse-tags-tooltip collapse-tags :remote-method="onSearch">
        <el-option v-for="it in labels" :label="it.name" :value="it.name" :key="it.id" />
      </el-select>
    </el-form-item>
    <el-form-item prop="world_id" label="关联世界">
      <el-select v-model="create_data.world_id" remote filterable reserve-keyword clearable
        :remote-method="onWorldSearch">
        <el-option v-for="it in worlds" :label="it.name" :value="it.id" :key="it.id" />
      </el-select>
    </el-form-item>
    <el-upload multiple :auto-upload="false" accept=".txt,.md,.markdown" v-model:file-list="create_data.files" :limit="20">
      <el-button type="primary">上传更多 [{{ create_data.nickname || '角色' }}] 的背景</el-button>
    </el-upload>
    <div class="flex item-center justify-center">
      <el-button @click="$emit('cancel')">取消</el-button>
      <el-button type="success" native-type="submit" :loading="loading.upload">确认</el-button>
    </div>
  </el-form>
</template>
<script setup lang="ts">
import type { LabelResponse, CharacterCreateForm, CharacterResponse } from '@/schemas/character';
import characterApi from '@/api/character';
import { computed, reactive, ref } from 'vue';
import { ElMessage, type UploadFile } from 'element-plus';
import { objectToFormData } from '@/utils';

const create_data = reactive<CharacterCreateForm>({
  nickname: '',
  description: '',
  first_message: "",
  data_range: 'all',
  labels: [],
  world_id: undefined,
  files: [],
  avatar: undefined,
});

interface Emits {
  (e: 'cancel'): void,
  (e: 'submit', data: CharacterResponse): void
}

const emits = defineEmits<Emits>();

// 头像预览URL
const avatarPreview = ref('');

// const avatar = ref<UploadFile>()
// const files = ref<UploadFile[]>([])
const labels = ref<LabelResponse[]>([])
const worlds = ref<LabelResponse[]>([])
const loading = reactive({
  labels: false,
  upload: false
})

const showAvatarPerview = computed(() =>
  (avatarPreview.value || '/default_avatar.webp')
)

const onSearch = async (query: string) => {
  if (query.length === 0) return [];
  loading.labels = true;
  try {
    labels.value = await characterApi.label.stream(query)
  } finally {
    loading.labels = false
  }
}

const onWorldSearch = async (query: string) => {
  if (query.length === 0) return [];
  loading.labels = true;
  try {
    worlds.value = await characterApi.world.stream(query)
  } finally {
    loading.labels = false
  }
}

const handleAvatarChange = (file: UploadFile) => {
  if (!file || !file.raw) return;
  create_data.avatar = file.raw
  const reader = new FileReader()
  reader.onload = (e) => {
    if (e.target?.result) {
      avatarPreview.value = e.target.result as string
    }
  }
  reader.readAsDataURL(file.raw)
}

const onSubmit = () => {
  if (create_data.nickname.length < 2) {
    ElMessage.info('请输入正确的名称')
    return;
  } else if (!create_data.description || create_data.description.length < 2) {
    ElMessage.info('请输入正确的描述')
    return;
  } else if (!create_data.first_message || create_data.first_message.length < 2) {
    ElMessage.info('请输入正确的消息')
    return;
  }
  create_data.files = create_data.files.map(it => it.raw)
  const form = objectToFormData(create_data)
  loading.upload = true;
  characterApi.create(form).then(res => {
    emits('submit', res)
  }).finally(() => {
    loading.upload = false;
  })
}

</script>
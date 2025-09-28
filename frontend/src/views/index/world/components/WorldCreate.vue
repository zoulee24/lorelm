<template>
  <el-form @submit.prevent="onSubmit">
    <el-form-item prop="nickname" label="名称">
      <el-input v-model="create_data.nickname" maxlength="16"></el-input>
    </el-form-item>
    <el-form-item prop="description" label="描述">
      <el-input type="textarea" v-model="create_data.description" :autosize="{minRows: 3, maxRows: 6}" resize="none" show-word-limit></el-input>
    </el-form-item>
    <el-form-item prop="data_range" label="可见访问">
      <el-select v-model="create_data.data_range">
        <el-option label="公开" value="all"></el-option>
        <el-option label="私有" value="self"></el-option>
      </el-select>
    </el-form-item>
    <el-form-item prop="labels" label="标签">
      <el-select v-model="create_data.labels" 
        multiple allow-create remote filterable reserve-keyword 
        clearable collapse-tags-tooltip collapse-tags
        :remote-method="onSearch">
        <el-option v-for="it in labels" :label="it.name" :value="it.id" :key="it.id" />
      </el-select>
    </el-form-item>
    <el-upload multiple :auto-upload="false" accept=".txt,.md,.markdown">
      <el-button type="primary">上传更多 [{{create_data.nickname || '世界'}}] 的背景</el-button>
    </el-upload>
    <div class="flex item-center justify-center">
      <el-button @click="$emit('cancel')" >取消</el-button>
      <el-button type="success" native-type="submit">确认</el-button>
    </div>
  </el-form>
</template>
<script setup lang="ts">
import type { LabelResponse, WorldCreateForm, WorldFullResponse } from '@/schemas/character';
import characterApi from '@/api/character';
import { reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
const create_data = reactive<WorldCreateForm>({
  nickname: '',
  description: '',
  data_range: 'all',
  labels: [],
});

interface Emits {
  (e: 'cancel'): void,
  (e: 'submit', data: WorldFullResponse): void
}

const emits = defineEmits<Emits>();

const labels = ref<LabelResponse[]>([])
const loading = reactive({
  labels: false
})

const onSearch = async (query: string) => {
  if (query.length === 0) return [];
  loading.labels = true;
  try {
    labels.value = await characterApi.label.stream(query)
  } finally {
    loading.labels = false
  }
}

const onSubmit = () => {
  if (create_data.nickname.length < 2) {
    ElMessage.info('请输入正确的名称')
    return;
  } else if (!create_data.description || create_data.description.length < 2) {
    ElMessage.info('请输入正确的描述')
    return;
  }
  characterApi.world.create(create_data).then(res => {
    emits('submit', res)
  })
}

</script>
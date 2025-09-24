<script lang="ts" setup>
import zhCN from 'element-plus/es/locale/lang/zh-cn.mjs'
</script>

<template>
  <el-config-provider :locale="zhCN">
    <router-view></router-view>
  </el-config-provider>
</template>

<style scoped>
</style>

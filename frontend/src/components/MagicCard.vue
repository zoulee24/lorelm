<template>
  <div class="magic-card-container" @mouseleave="handleContainerMouseLeave">
    <div class="magic-card" :class="{
      'is-hovered': isHovered,
      'is-active': isActive,
      [size]: true
    }" @mouseenter="handleCardMouseEnter">
      <div class="card-icon">
        <slot name="icon">
          <div class="default-icon">✨</div>
        </slot>
      </div>

      <div class="card-content">
        <div class="card-title">
          <slot></slot>
        </div>

        <div class="card-subtitle" v-if="$slots.subtitle">
          <slot name="subtitle"></slot>
        </div>
      </div>

      <div class="card-glow"></div>
    </div>

    <div class="card-description" :class="{ 'is-visible': showDescription }" v-if="description || $slots.description"
      @mouseenter="handleCardMouseEnter" @mouseleave="handleContainerMouseLeave">
      <slot name="description">
        <div class="default-description">{{ description }}</div>
      </slot>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'

const props = defineProps({
  description: {
    type: String,
    default: ''
  },
  active: {
    type: Boolean,
    default: false
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value: string) => ['small', 'medium', 'large'].includes(value)
  }
})

const emit = defineEmits(['mouseenter', 'mouseleave'])

const isHovered = ref(false)
const isActive = ref(props.active)
const showDescription = ref(false)
const descriptionHovered = ref(false)
let leave: null | number = null

const handleCardMouseEnter = () => {
  isHovered.value = true
  showDescription.value = true
  emit('mouseenter')
  if (leave) {
    clearTimeout(leave)
    leave = null;
  }
}

// 容器的mouseleave事件
const handleContainerMouseLeave = () => {
  if (descriptionHovered.value) return
  if (leave) clearTimeout(leave)

  leave = setTimeout(() => {
    isHovered.value = false
    showDescription.value = false
    emit('mouseleave')
    leave = null
  }, 100)
}
</script>

<style scoped>
.magic-card-container {
  position: relative;
  display: inline-block;
  margin: 0.5rem;
}

.magic-card {
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.magic-card.small {
  padding: 1rem;
  min-width: 160px;
  height: 100px;
}

.magic-card.medium {
  padding: 1.5rem;
  min-width: 200px;
  height: 120px;
}

.magic-card.large {
  padding: 2rem;
  min-width: 280px;
  height: 160px;
}

.magic-card.is-hovered {
  transform: translateY(-8px) scale(1.02);
  border-color: #ffd700;
  box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4);
}

.magic-card.is-active {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border-color: #fff;
}

.card-glow {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57, #ff9ff3);
  border-radius: 16px;
  opacity: 0;
  z-index: -1;
  transition: opacity 0.3s ease;
  background-size: 400% 400%;
  animation: gradient-rotate 3s ease infinite;
}

.magic-card.is-hovered .card-glow {
  opacity: 1;
}

@keyframes gradient-rotate {
  0% {
    background-position: 0% 50%;
  }

  50% {
    background-position: 100% 50%;
  }

  100% {
    background-position: 0% 50%;
  }
}

.card-icon {
  flex-shrink: 0;
  font-size: 2rem;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.default-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.card-content {
  flex: 1;
  color: white;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.card-subtitle {
  font-size: 0.875rem;
  opacity: 0.9;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.card-description {
  position: absolute;
  top: calc(100% + 1rem);
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 1rem;
  border-radius: 12px;
  font-size: 0.875rem;
  line-height: 1.5;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  opacity: 0;
  transform: translateY(-10px);
  transition: all 0.3s ease;
  z-index: 10;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
  pointer-events: none;
  max-height: 200px;
  overflow-y: auto;
  word-break: break-word;
}

.magic-card.large .card-description {
  max-height: 250px;
}

.magic-card.small .card-description {
  max-height: 150px;
}

.card-description::-webkit-scrollbar {
  width: 6px;
}

.card-description::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.card-description::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.card-description::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

.card-description.is-visible {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}

.default-description {
  /* text-align: center; */
}

@media (max-width: 640px) {
  .magic-card {
    min-width: 150px;
    height: 100px;
    padding: 1rem;
  }

  .card-title {
    font-size: 1rem;
  }

  .card-icon {
    font-size: 1.5rem;
  }
}
</style>
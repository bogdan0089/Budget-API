<template>
  <div class="app-select" :class="{ open: isOpen }" ref="selectRef">
    <button type="button" class="app-select__trigger" @click="isOpen = !isOpen">
      <span>{{ selectedLabel }}</span>
      <i class="bi bi-chevron-down app-select__arrow"></i>
    </button>
    <div v-if="isOpen" class="app-select__dropdown">
      <div
        v-for="opt in options"
        :key="opt.value"
        class="app-select__option"
        :class="{ selected: opt.value === modelValue }"
        @click="select(opt.value)"
      >
        <i v-if="opt.icon" :class="opt.icon" class="me-2"></i>
        {{ opt.label }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  modelValue: String,
  options: Array,
})
const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)
const selectRef = ref(null)

const selectedLabel = computed(
  () => props.options.find((o) => o.value === props.modelValue)?.label || props.options[0]?.label || '',
)

function select(value) {
  emit('update:modelValue', value)
  isOpen.value = false
}

function onClickOutside(e) {
  if (selectRef.value && !selectRef.value.contains(e.target)) isOpen.value = false
}

onMounted(() => document.addEventListener('mousedown', onClickOutside))
onUnmounted(() => document.removeEventListener('mousedown', onClickOutside))
</script>

<style scoped>
.app-select {
  position: relative;
}

.app-select__trigger {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1.5px solid #e2e8f0;
  background: #fff;
  font-size: 0.9rem;
  color: #1e293b;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.app-select.open .app-select__trigger {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}

.app-select__arrow {
  font-size: 0.75rem;
  color: #94a3b8;
  transition: transform 0.2s;
}

.app-select.open .app-select__arrow {
  transform: rotate(180deg);
}

.app-select__dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  border: 1.5px solid #e2e8f0;
  z-index: 200;
  overflow: hidden;
}

.app-select__option {
  padding: 10px 14px;
  font-size: 0.875rem;
  cursor: pointer;
  color: #1e293b;
  transition: background 0.15s;
}

.app-select__option:hover {
  background: #f1f5f9;
}

.app-select__option.selected {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
}
</style>

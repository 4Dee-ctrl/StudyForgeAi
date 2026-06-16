<script setup>
import { computed } from 'vue'

const model = defineModel({ type: String, default: '' })

const countClass = computed(() => {
  if (model.value.length > 50000) return 'danger'
  if (model.value.length > 45000) return 'warning'
  return ''
})
</script>

<template>
  <section class="input-panel">
    <div class="section-title-row">
      <div>
        <h2>Source Material</h2>
        <p>Paste notes, readings, or extracted file text.</p>
      </div>
      <button class="ghost-button" type="button" :disabled="!model" @click="model = ''">Clear</button>
    </div>

    <label class="sr-only" for="source-text">Source text</label>
    <textarea
      id="source-text"
      v-model="model"
      class="source-textarea"
      maxlength="52000"
      placeholder="Paste at least 50 characters of study material here..."
    />

    <div class="input-meta">
      <span :class="['char-count', countClass]">{{ model.length.toLocaleString() }} / 50,000</span>
      <span v-if="model.length > 0 && model.trim().length < 50">Minimum 50 characters required.</span>
      <span v-else-if="model.length > 50000">Text exceeds the backend limit.</span>
    </div>
  </section>
</template>

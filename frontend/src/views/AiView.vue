<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import FileUpload from '../components/FileUpload.vue'
import TextInput from '../components/TextInput.vue'
import { STUDY_AID_TYPES, useStudyStore } from '../stores/study'

const store = useStudyStore()
const router = useRouter()
const inputMode = ref('paste')

const progressItems = computed(() =>
  STUDY_AID_TYPES.filter((type) => store.selectedTypes.includes(type.id)).map((type) => ({
    ...type,
    status: store.generationProgress[type.id] || 'waiting',
  })),
)

async function generate() {
  const ok = await store.generateAll()
  if (ok) {
    router.push('/results')
  }
}
</script>

<template>
  <section class="tool-view">
    <div class="hero-band">
      <div>
        <p class="eyebrow">AI Tool</p>
        <h1>Turn course material into usable study aids.</h1>
        <p class="hero-copy">Paste text or extract it from a PDF/PPTX, then generate summaries, key terms, quizzes, and guides.</p>
      </div>
    </div>

    <div v-if="store.error" class="alert" role="alert">{{ store.error }}</div>

    <div class="mode-tabs" role="tablist" aria-label="Input mode">
      <button type="button" :class="{ active: inputMode === 'paste' }" @click="inputMode = 'paste'">Paste Text</button>
      <button type="button" :class="{ active: inputMode === 'upload' }" @click="inputMode = 'upload'">Upload File</button>
    </div>

    <TextInput v-if="inputMode === 'paste'" v-model="store.sourceText" />
    <FileUpload v-else @extracted="inputMode = 'paste'" />

    <section class="input-panel">
      <div class="section-title-row">
        <div>
          <h2>Study Aid Types</h2>
          <p>Select at least one output.</p>
        </div>
      </div>

      <div class="type-grid">
        <label v-for="type in STUDY_AID_TYPES" :key="type.id" class="type-option">
          <input
            type="checkbox"
            :checked="store.selectedTypes.includes(type.id)"
            @change="store.toggleType(type.id)"
          />
          <span>{{ type.label }}</span>
        </label>
      </div>
    </section>

    <section v-if="store.isGenerating" class="progress-panel" aria-live="polite">
      <div v-for="item in progressItems" :key="item.id" :class="['progress-item', item.status]">
        <span>{{ item.status === 'done' ? '✓' : item.status === 'error' ? '!' : '•' }}</span>
        <strong>{{ item.label }}</strong>
        <small>{{ item.status }}</small>
      </div>
    </section>

    <div class="action-row">
      <button class="primary-button" type="button" :disabled="!store.canGenerate" @click="generate">
        {{ store.isGenerating ? 'Generating...' : 'Generate Study Aids' }}
      </button>
    </div>
  </section>
</template>
